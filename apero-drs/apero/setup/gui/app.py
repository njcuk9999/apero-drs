#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The APERO setup browser gui (apero_setup.py --gui)

An APERO specific application on top of the generic aperocore.gui framework
(the same framework as pogos_gui and apero_queue). Tabs:

    Info      what each tab does (shared with the apero-ri docs)
    Setup     apero_setup.py from a form (profile, instrument, data
              directories, external raw data, database, plots / cleaning)
              down to "Validate and save"
    Edit      the files apero_setup wrote to DRS_UCONFIG (form or raw text,
              review the diff, save with a backup) and re-running setup
              with the edited values (apero_setup.py --update)
    Validate  apero_validate.py and a graphical state report of a profile
              (config files, paths, databases, python modules, machine)
              exported as a single text file
    Docs      every APERO constant / keyword (per instrument) and the
              APERO guides (the same markdown pages apero-ri serves)

Every action runs the real APERO script (questions it still asks are
answered in the browser console), so the gui never duplicates setup logic.

Created on 2026-11-27

@author: cook
"""
import json
import os
import re
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from aperocore import drs_lang
from aperocore.base import base
from aperocore.gui import files as gui_files
from aperocore.gui import webapp

from apero.setup.core import drs_setup
from apero.setup.gui import commands
from apero.setup.gui import probe

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero.setup.gui.app.py'
# the APERO version (drs_setup.__version__ is the apero-core version)
__version__ = commands.apero_version()
# get the text entry function
textentry = drs_lang.textentry
# the directory with the gui page / assets
STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')
# the page template
TEMPLATE_PATH = os.path.join(STATIC_DIR, 'setup_gui.html')
# environment variable for the supervised worker port
WORKER_ENV = 'APERO_SETUP_GUI_WORKER_PORT'
# the gui state (process registry, job logs, backups, reports)
STATE_DIR = os.path.expanduser('~/.apero/setup_gui')
# the activity log / console channels (one per page)
CHANNELS = ['setup', 'edit', 'validate', 'data', 'main']
# seconds a probe may run
PROBE_TIMEOUT = 600
# the apero-ri documentation tree (repository checkout only)
DOC_ROOT = Path(__file__).resolve().parents[4].joinpath('documentation',
                                                       'ari')
# the guides shown on the Docs tab (page ref -> title) - the Info tab is
#   the first one
GUIDES = [('reference/setup_gui', 'APERO setup gui'),
          ('install', 'Installation'),
          ('apero/user_tools/valid', 'apero_validate'),
          ('reference/mysql', 'MySQL databases'),
          ('reference/developer_environments', 'Developer environments')]
# yaml front matter at the start of a markdown page
FRONT_MATTER = re.compile(r'^---\s*\n.*?\n---\s*\n', flags=re.DOTALL)
# markdown links to other docs pages (rendered as Docs tab links)
DOC_LINK = re.compile(r'\[([^\]]+)\]\((?!https?://)([^)\s#]+)[^)]*\)')
# the rendered link tokens (see render_guide)
DOC_TOKEN = re.compile(r'XXDOC([\w./-]+)XX(.*?)XXEND')


# =============================================================================
# Define classes
# =============================================================================
class SetupGuiApp(webapp.GuiApp):
    """
    The APERO setup gui application (see module doc string)
    """
    name = 'APERO setup'
    template_path = TEMPLATE_PATH
    app_static_dir = STATIC_DIR
    icon_name = 'apero_icon.ico'
    worker_env = WORKER_ENV
    channels = CHANNELS

    def __init__(self, initial: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialise the setup gui

        :param initial: dict or None, setup form values from the command
                        line (e.g. --name / --config / --instrument)

        :return: None
        """
        # setup form values given on the command line
        self.initial = initial or dict()
        # the constant descriptions (Docs tab) - probed once
        self.param_info: Optional[Dict[str, Any]] = None
        self.param_lock = threading.Lock()
        # the last state report of each profile
        self.reports: Dict[str, Dict[str, Any]] = dict()
        self.report_lock = threading.Lock()
        # config files before re-running setup (profile -> name -> text)
        self.snapshots: Dict[str, Dict[str, Optional[str]]] = dict()
        # profiles opened in the Data tab that are not in profiles.ini
        self.data_profiles: List[str] = []
        os.makedirs(STATE_DIR, exist_ok=True)
        super().__init__()

    # -------------------------------------------------------------------------
    # framework overrides
    # -------------------------------------------------------------------------
    def state_dir(self) -> Optional[str]:
        """
        Get the gui state directory (~/.apero/setup_gui)

        :return: str, the state directory
        """
        return STATE_DIR

    def _profile_paths(self) -> List[str]:
        """
        Get every profile the gui knows: registered ones (profiles.ini) and
        those opened in the Data tab

        :return: list of str, the profile directories
        """
        paths = [info['path'] for info in commands.list_profiles()
                 if info['exists']]
        for path in self.data_profiles:
            if path not in paths:
                paths.append(path)
        return paths

    def _data_dirs(self) -> List[Dict[str, Any]]:
        """
        Get the data directories of every known profile (setup run)

        :return: list of dict, see commands.data_dirs
        """
        out: List[Dict[str, Any]] = []
        for path in self._profile_paths():
            try:
                out += commands.data_dirs(path)
            except commands.CommandError:
                continue
        return out

    def file_roots(self) -> List[str]:
        """
        Get the directories the gui may read in: the gui state, every
        known profile (DRS_UCONFIG) and the data directories of the
        profiles setup has been run for (Data tab)

        :return: list of str, the roots
        """
        roots = [STATE_DIR]
        for path in self._profile_paths():
            if path not in roots:
                roots.append(path)
        for info in self._data_dirs():
            if info['exists'] and info['path'] not in roots:
                roots.append(info['path'])
        return roots

    def protected_roots(self) -> List[str]:
        """
        Get the directories nothing may be deleted from (raw data)

        :return: list of str, the protected directories
        """
        return [info['path'] for info in self._data_dirs()
                if info['protected']]

    def page_tokens(self) -> Dict[str, str]:
        """
        Get the page template tokens

        :return: dict, token -> text
        """
        info = render_guide(GUIDES[0][0])
        return dict(VERSION=__version__, INFO=info['html'],
                    INITIAL=json.dumps(self.initial, default=str))

    def get_runtime_info(self) -> Dict[str, Any]:
        """
        Add the APERO version to the runtime information

        :return: dict, the runtime information
        """
        info = super().get_runtime_info()
        info['apero_version'] = __version__
        info['apero_source'] = str(commands.APERO_DIR)
        info['state_dir'] = STATE_DIR
        return info

    # -------------------------------------------------------------------------
    # routes
    # -------------------------------------------------------------------------
    def add_routes(self) -> None:
        """
        Register the setup gui routes

        :return: None
        """
        get, post = self.add_get, self.add_post
        get('/api/setup/choices',
            lambda req: webapp.Response.json(commands.setup_choices()))
        get('/api/setup/profiles',
            lambda req: webapp.Response.json(dict(
                profiles=commands.list_profiles())))
        post('/api/setup/profile_form', self.api_profile_form)
        post('/api/setup/preview', self.api_preview)
        post('/api/setup/run', self.api_run)
        post('/api/setup/update', self.api_update)
        get('/api/setup/rerun_diff', self.api_rerun_diff)
        get('/api/setup/file', self.api_file)
        post('/api/setup/file_save', self.api_file_save)
        get('/api/setup/backups', self.api_backups)
        post('/api/setup/data_dirs', self.api_data_dirs)
        post('/api/setup/dir_stats', self.api_dir_stats)
        post('/api/setup/reset', self.api_reset)
        get('/api/setup/params', self.api_params)
        post('/api/setup/report', self.api_report)
        post('/api/setup/report_save', self.api_report_save)
        post('/api/setup/validate', self.api_validate)
        get('/api/setup/guides', self.api_guides)
        get('/api/setup/guide', self.api_guide)

    # -------------------------------------------------------------------------
    # helpers
    # -------------------------------------------------------------------------
    def _start(self, channel: str, kind: str, built: Dict[str, Any],
               cwd: Optional[str] = None, on_done: Any = None
               ) -> webapp.Response:
        """
        Start a built command as the (interactive) job of a channel

        :param channel: str, the console channel
        :param kind: str, the process kind
        :param built: dict(cmd, display, env), see commands
        :param cwd: str or None, working directory (default: state dir)
        :param on_done: callable or None, called with the return code

        :return: Response, json dict(started, message, display)
        """
        # gui jobs never open plot windows
        env = dict(MPLBACKEND='Agg', PYTHONUNBUFFERED='1')
        env.update(built.get('env') or dict())
        jkwargs = dict(label=built['display'], cwd=cwd or STATE_DIR,
                       env=env, interactive=True, on_done=on_done)
        result = self.jobs.start(channel, kind, built['cmd'], **jkwargs)
        result['display'] = built['display']
        return webapp.Response.json(result)

    def _run_probe(self, kind: str, profile: str) -> Dict[str, Any]:
        """
        Run an apero.setup.gui.probe sub process and decode its result

        :param kind: str, params or report
        :param profile: str, the DRS_UCONFIG directory to use

        :return: dict, the probe result (dict(error) on failure)
        """
        cmd = [sys.executable, '-m', 'apero.setup.gui.probe', kind]
        env = dict(os.environ, PYTHONUNBUFFERED='1', MPLBACKEND='Agg')
        env[base.USER_ENV] = profile
        try:
            output = subprocess.run(cmd, capture_output=True, text=True,
                                    timeout=PROBE_TIMEOUT, cwd=STATE_DIR,
                                    stdin=subprocess.DEVNULL, env=env)
        except (OSError, subprocess.SubprocessError) as error:
            return dict(error=str(error))
        for line in reversed(output.stdout.splitlines()):
            if line.startswith(probe.RESULT_PREFIX):
                return json.loads(line[len(probe.RESULT_PREFIX):])
        tail = (output.stdout + output.stderr).strip().splitlines()[-12:]
        return dict(error=str(textentry('SETUP_GUI_PROBE_FAILED',
                                        args=['\n'.join(tail)])))

    def _docs_profile(self) -> str:
        """
        Get a profile for the constants probe: the first valid registered
        profile, else a throw away one in the state directory (the
        instrument definitions only need DRS_UCONFIG to import)

        :return: str, a DRS_UCONFIG directory
        """
        for info in commands.list_profiles():
            if info.get('valid'):
                return info['path']
        path = os.path.join(STATE_DIR, 'docs_profile')
        os.makedirs(path, exist_ok=True)
        install = {'OBS.INSTRUMENT': 'SPIROU', 'GLOBAL.LANGUAGE':
                   str(base.DEFAULT_LANG), base.USER_ENV: path}
        with open(os.path.join(path, base.INSTALL_YAML), 'w') as ifile:
            yaml.safe_dump(install, ifile)
        with open(os.path.join(path, base.DATABASE_YAML), 'w') as dfile:
            yaml.safe_dump(dict(TYPE='mysql+pymysql'), dfile)
        return path

    @staticmethod
    def _error(error: Exception) -> webapp.Response:
        """
        Turn a command error into a json error response

        :param error: Exception, the error

        :return: Response, the error response
        """
        return webapp.Response.error(str(error))

    # -------------------------------------------------------------------------
    # setup routes
    # -------------------------------------------------------------------------
    def api_profile_form(self, request: webapp.Request) -> webapp.Response:
        """
        POST /api/setup/profile_form {profile}: the setup form values of an
        existing profile (password never included)

        :param request: Request, the request

        :return: Response, json dict(form)
        """
        try:
            form = commands.profile_form(request.arg('profile'))
        except commands.CommandError as error:
            return self._error(error)
        return webapp.Response.json(dict(form=form))

    def _build(self, action: str, request: webapp.Request
               ) -> Dict[str, Any]:
        """
        Build the command of one gui action

        :param action: str, setup / update / install_sh / validate
        :param request: Request, the request (form / profile)

        :raises CommandError: for invalid forms

        :return: dict(cmd, display, env, profile)
        """
        profile = request.arg('profile')
        if action == 'setup':
            return commands.setup_command(request.arg('form', dict()) or {})
        if action in ['update', 'install_sh']:
            return commands.update_command(profile,
                                           install_sh=action == 'install_sh')
        if action == 'reset':
            return commands.reset_command(profile, request.arg('part', 'all'),
                                          ask=bool(request.arg('ask', True)),
                                          nolog=bool(request.arg('nolog',
                                                                 False)))
        if action == 'validate':
            reportfile = None
            if request.arg('report', False):
                reportfile = self._report_path(profile)
            return commands.validate_command(profile, reportfile)
        raise commands.CommandError(str(textentry(
            'SETUP_GUI_UNKNOWN', args=['action', action])))

    def api_preview(self, request: webapp.Request) -> webapp.Response:
        """
        POST /api/setup/preview {action, form|profile}: the cli equivalent
        of an action (or why the form is not valid yet)

        :param request: Request, the request

        :return: Response, json dict(display, errors, profile, exists)
        """
        action = str(request.arg('action', ''))
        try:
            built = self._build(action, request)
        except commands.CommandError as error:
            errors = [line for line in str(error).splitlines() if line]
            return webapp.Response.json(dict(display='', errors=errors))
        profile = built.get('profile')
        exists = bool(profile) and os.path.isfile(
            os.path.join(profile, base.INSTALL_YAML))
        return webapp.Response.json(dict(display=built['display'],
                                         errors=[], profile=profile,
                                         exists=exists))

    def api_run(self, request: webapp.Request) -> webapp.Response:
        """
        POST /api/setup/run {form}: run apero_setup.py (console)

        :param request: Request, the request

        :return: Response, json dict(started, message, display)
        """
        try:
            built = self._build('setup', request)
        except commands.CommandError as error:
            return self._error(error)
        return self._start('setup', 'apero_setup', built)

    def api_update(self, request: webapp.Request) -> webapp.Response:
        """
        POST /api/setup/update {profile, install_sh}: re-run setup of a
        profile with the values in its files (or only regenerate
        install_script.sh) - the files are kept to show what changed

        :param request: Request, the request

        :return: Response, json dict(started, message, display)
        """
        install_sh = bool(request.arg('install_sh', False))
        action = 'install_sh' if install_sh else 'update'
        try:
            built = self._build(action, request)
            self.snapshots[built['profile']] = commands.snapshot(
                built['profile'])
        except commands.CommandError as error:
            return self._error(error)
        return self._start('edit', 'apero_setup_' + action, built)

    def api_rerun_diff(self, request: webapp.Request) -> webapp.Response:
        """
        GET /api/setup/rerun_diff?profile=: the config files that changed
        since the last re-run started (old and new text)

        :param request: Request, the request

        :return: Response, json dict(changed=list of dict(name, old, new))
        """
        try:
            profile = commands.check_profile(request.arg('profile'))
            now = commands.snapshot(profile)
        except commands.CommandError as error:
            return self._error(error)
        before = self.snapshots.get(profile, dict())
        changed = [dict(name=name, old=before.get(name) or '',
                        new=now.get(name) or '')
                   for name in now if before.get(name) != now.get(name)]
        return webapp.Response.json(dict(changed=changed,
                                         snapshot=bool(before)))

    # -------------------------------------------------------------------------
    # edit routes
    # -------------------------------------------------------------------------
    def api_file(self, request: webapp.Request) -> webapp.Response:
        """
        GET /api/setup/file?profile=&name=: one config file of a profile

        :param request: Request, the request

        :return: Response, json dict(path, text, mtime, editable, exists,
                 instrument)
        """
        try:
            outs = commands.config_file(request.arg('profile'),
                                        request.arg('name'))
        except commands.CommandError as error:
            return self._error(error)
        path, editable = outs
        # the profile instrument (defaults shown in the Edit tab)
        info = commands.profile_info(os.path.dirname(path))
        instrument = info.get('instrument')
        if not os.path.isfile(path):
            return webapp.Response.json(dict(path=path, text='', mtime=None,
                                             editable=editable,
                                             exists=False,
                                             instrument=instrument))
        data = gui_files.read_text(path, None)
        data.update(editable=editable, exists=True,
                    mtime=os.path.getmtime(path), instrument=instrument)
        return webapp.Response.json(data)

    def _backup_dir(self, path: str) -> str:
        """
        Get the backup directory of a config file

        :param path: str, the config file

        :return: str, ~/.apero/setup_gui/backups/{profile}
        """
        profile = os.path.basename(os.path.dirname(path))
        return os.path.join(STATE_DIR, 'backups', profile)

    def api_file_save(self, request: webapp.Request) -> webapp.Response:
        """
        POST /api/setup/file_save {profile, name, text, mtime, force}: save
        a config file (a backup is kept); refuses if the file changed on
        disk since it was loaded unless forced

        :param request: Request, the request

        :return: Response, json dict(success, message, mtime, conflict)
        """
        try:
            outs = commands.config_file(request.arg('profile'),
                                        request.arg('name'))
        except commands.CommandError as error:
            return self._error(error)
        path, editable = outs
        if not editable:
            return webapp.Response.error(str(textentry(
                'SETUP_GUI_NOT_CONFIG_FILE', args=[request.arg('name')])))
        loaded = request.arg('mtime', None)
        if (os.path.exists(path) and loaded is not None
                and not request.arg('force', False)):
            if abs(os.path.getmtime(path) - float(loaded)) > 1e-3:
                return webapp.Response.json(dict(
                    success=False, conflict=True,
                    message=str(textentry('SETUP_GUI_CONFLICT'))))
        text = str(request.arg('text', ''))
        wkwargs = dict(backup_dir=self._backup_dir(path))
        result = gui_files.write_text(path, text, None, **wkwargs)
        backup = os.path.basename(result['backup'] or '') or '-'
        message = str(textentry('SETUP_GUI_SAVED', args=[path, backup]))
        self.state.add_message(message, 'edit')
        self.state.bump()
        return webapp.Response.json(dict(success=True, message=message,
                                         mtime=os.path.getmtime(path)))

    def api_backups(self, request: webapp.Request) -> webapp.Response:
        """
        GET /api/setup/backups?profile=&name=: the gui backups of a file

        :param request: Request, the request

        :return: Response, json dict(backups=list of dict(path, mtime))
        """
        try:
            outs = commands.config_file(request.arg('profile'),
                                        request.arg('name'))
        except commands.CommandError as error:
            return self._error(error)
        path = outs[0]
        directory = self._backup_dir(path)
        backups = []
        if os.path.isdir(directory):
            for fname in os.listdir(directory):
                if fname.startswith(os.path.basename(path)):
                    full = os.path.join(directory, fname)
                    backups.append(dict(path=full,
                                        mtime=os.path.getmtime(full)))
        backups.sort(key=lambda item: -item['mtime'])
        return webapp.Response.json(dict(backups=backups))

    # -------------------------------------------------------------------------
    # data manager routes
    # -------------------------------------------------------------------------
    def api_data_dirs(self, request: webapp.Request) -> webapp.Response:
        """
        POST /api/setup/data_dirs {profile}: the data directories of a
        profile (the profile may then be browsed)

        :param request: Request, the request

        :return: Response, json dict(profile, dirs, reset_parts)
        """
        try:
            path = commands.check_setup_done(request.arg('profile'))
            dirs = commands.data_dirs(path)
        except commands.CommandError as error:
            return self._error(error)
        # allow browsing a profile chosen on disk (not in profiles.ini)
        if path not in self._profile_paths():
            self.data_profiles.append(path)
        return webapp.Response.json(dict(
            profile=path, dirs=dirs, reset_parts=commands.reset_choices()))

    def api_dir_stats(self, request: webapp.Request) -> webapp.Response:
        """
        POST /api/setup/dir_stats {path}: number of files and size below a
        data directory (stops after a time limit)

        :param request: Request, the request

        :return: Response, json dict(nfiles, size, complete)
        """
        try:
            real = gui_files.check_path(str(request.arg('path', '')),
                                        self.file_roots())
        except gui_files.FileAccessError as error:
            return webapp.Response.error(str(error), 403)
        return webapp.Response.json(commands.dir_stats(real))

    def api_fs_delete(self, request: webapp.Request) -> webapp.Response:
        """
        POST /api/fs/delete {paths}: delete files (as the framework) but
        never anything in a raw data directory

        :param request: Request, the request

        :return: Response, json dict(success, message, deleted)
        """
        paths = request.arg('paths', []) or []
        if not isinstance(paths, list):
            paths = [paths]
        protected = self.protected_roots()
        for path in paths:
            # the path itself (links) and what it points to
            absolute = os.path.abspath(os.path.expanduser(str(path)))
            real = os.path.realpath(absolute)
            for root in protected:
                if (gui_files.is_within(absolute, root)
                        or gui_files.is_within(real, root)):
                    return webapp.Response.error(str(textentry(
                        'SETUP_GUI_PROTECTED', args=[absolute])), 403)
        return super().api_fs_delete(request)

    def api_reset(self, request: webapp.Request) -> webapp.Response:
        """
        POST /api/setup/reset {profile, part, ask, nolog}: run
        apero_reset.py for a profile (console)

        :param request: Request, the request

        :return: Response, json dict(started, message, display)
        """
        try:
            built = self._build('reset', request)
        except commands.CommandError as error:
            return self._error(error)
        # reports of this profile are out of date after a reset
        self.reports.pop(built['profile'], None)
        return self._start('data', 'apero_reset', built)

    # -------------------------------------------------------------------------
    # docs routes
    # -------------------------------------------------------------------------
    def api_params(self, request: webapp.Request) -> webapp.Response:
        """
        GET /api/setup/params: every constant / keyword with its value for
        every instrument (probed once and cached - a few seconds)

        :param request: Request, the request

        :return: Response, json (see probe.probe_params)
        """
        _ = request
        with self.param_lock:
            if self.param_info is None:
                result = self._run_probe('params', self._docs_profile())
                if 'error' in result:
                    return webapp.Response.error(result['error'])
                self.param_info = result
            return webapp.Response.json(self.param_info)

    def api_guides(self, request: webapp.Request) -> webapp.Response:
        """
        GET /api/setup/guides: the guides available on the Docs tab

        :param request: Request, the request

        :return: Response, json dict(guides=list of dict(ref, title))
        """
        _ = request
        guides = [dict(ref=ref, title=title) for ref, title in GUIDES
                  if find_guide(ref) is not None]
        return webapp.Response.json(dict(guides=guides,
                                         root=str(DOC_ROOT)))

    def api_guide(self, request: webapp.Request) -> webapp.Response:
        """
        GET /api/setup/guide?ref=: one guide rendered to html

        :param request: Request, the request

        :return: Response, json dict(ref, html, path)
        """
        return webapp.Response.json(render_guide(str(request.arg('ref',
                                                                 ''))))

    # -------------------------------------------------------------------------
    # validate routes
    # -------------------------------------------------------------------------
    def _report_path(self, profile: Any) -> str:
        """
        Get a new state report file name for a profile

        :param profile: Any, the profile directory

        :return: str, ~/.apero/setup_gui/reports/apero_report_*.txt
        """
        from apero.tools.module.setup import drs_report
        directory = os.path.join(STATE_DIR, 'reports')
        return drs_report.default_report_path(str(profile), directory)

    def api_report(self, request: webapp.Request) -> webapp.Response:
        """
        POST /api/setup/report {profile, refresh}: the state report of a
        profile (cached until refreshed)

        :param request: Request, the request

        :return: Response, json dict(report, text, collected)
        """
        try:
            profile = commands.check_profile(request.arg('profile'))
        except commands.CommandError as error:
            return self._error(error)
        refresh = bool(request.arg('refresh', False))
        with self.report_lock:
            if refresh or profile not in self.reports:
                result = self._run_probe('report', profile)
                if 'error' in result:
                    return webapp.Response.error(result['error'])
                result['collected'] = time.time()
                self.reports[profile] = result
            return webapp.Response.json(self.reports[profile])

    def api_report_save(self, request: webapp.Request) -> webapp.Response:
        """
        POST /api/setup/report_save {profile}: write the last state report
        of a profile to a text file

        :param request: Request, the request

        :return: Response, json dict(success, path, message)
        """
        try:
            profile = commands.check_profile(request.arg('profile'))
        except commands.CommandError as error:
            return self._error(error)
        report = self.reports.get(profile)
        if report is None:
            return webapp.Response.error(str(textentry(
                'SETUP_GUI_REQUIRED', args=['report'])))
        path = self._report_path(profile)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as rfile:
            rfile.write(report['text'])
        message = str(textentry('40-510-00061', args=[path]))
        self.state.add_message(message, 'validate')
        return webapp.Response.json(dict(success=True, path=path,
                                         message=message))

    def api_validate(self, request: webapp.Request) -> webapp.Response:
        """
        POST /api/setup/validate {profile, report}: run apero_validate.py
        for a profile (console)

        :param request: Request, the request

        :return: Response, json dict(started, message, display)
        """
        try:
            built = self._build('validate', request)
        except commands.CommandError as error:
            return self._error(error)
        return self._start('validate', 'apero_validate', built,
                           cwd=os.path.join(STATE_DIR))


# =============================================================================
# Define functions
# =============================================================================
def doc_version_dir() -> Optional[Path]:
    """
    Get the documentation directory of the default (first) docs version

    :return: Path or None, documentation/ari/{version} (None if the
             documentation tree is not available, e.g. a non editable
             install)
    """
    versions_file = DOC_ROOT.joinpath('versions.yaml')
    if not versions_file.is_file():
        return None
    with open(versions_file, 'r', encoding='utf-8') as vfile:
        versions = (yaml.safe_load(vfile) or dict()).get('versions') or []
    if not versions:
        return None
    return DOC_ROOT.joinpath(str(versions[0]['id']))


def find_guide(ref: str) -> Optional[Path]:
    """
    Find the markdown file of a docs page (the same lookup as apero-ri:
    version page, version index, shared page, shared index)

    :param ref: str, the page reference (e.g. reference/setup_gui)

    :return: Path or None, the markdown file
    """
    version_dir = doc_version_dir()
    ref = str(ref).strip('/')
    # only plain relative references (no "..")
    if version_dir is None or not ref or '..' in ref.split('/'):
        return None
    candidates = []
    for base_dir in [version_dir, DOC_ROOT.joinpath('all')]:
        docs = base_dir.joinpath('home', 'docs')
        candidates += [docs.joinpath(ref + '.md'),
                       docs.joinpath(ref, 'index.md')]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def render_guide(ref: str) -> Dict[str, Any]:
    """
    Render one docs page (front matter removed, links to other docs pages
    become Docs tab links)

    :param ref: str, the page reference

    :return: dict(ref, html, path)
    """
    path = find_guide(ref)
    if path is None:
        html = ('<p>The APERO documentation is not available in this '
                'installation ({0}). See the APERO documentation on '
                'apero-ri.</p>'.format(DOC_ROOT))
        return dict(ref=ref, html=html, path=None)
    text = FRONT_MATTER.sub('', path.read_text(encoding='utf-8'), count=1)
    # relative docs links: a token that survives the markdown escaping
    text = DOC_LINK.sub(lambda match: 'XXDOC{0}XX{1}XXEND'.format(
        _doc_ref(ref, match.group(2)), match.group(1)), text)
    html = render_markdown(text)
    # the tokens become links to the page on the Docs tab
    html = DOC_TOKEN.sub(r'<a class="doc-link" data-guide="\1">\2</a>',
                         html)
    return dict(ref=ref, html=html, path=str(path))


def render_markdown(text: str) -> str:
    """
    Render markdown with the shared renderer (webapp.render_markdown),
    adding the pipe tables the APERO docs pages use

    :param text: str, the markdown text

    :return: str, the html
    """
    # split the text into table blocks and everything else (tables inside
    #   fenced code blocks are left alone)
    parts: List[str] = []
    other: List[str] = []
    table: List[str] = []
    in_code = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith('```'):
            in_code = not in_code
        if not in_code and stripped.startswith('|'):
            if other:
                parts.append(webapp.render_markdown('\n'.join(other)))
                other = []
            table.append(stripped)
            continue
        if table:
            parts.append(_markdown_table(table))
            table = []
        other.append(line)
    if table:
        parts.append(_markdown_table(table))
    if other:
        parts.append(webapp.render_markdown('\n'.join(other)))
    return '\n'.join(parts)


def _markdown_table(rows: List[str]) -> str:
    """
    Render the rows of a markdown pipe table to html (a "|---|" row after
    the first row makes the first row the header)

    :param rows: list of str, the table lines (each starts with "|")

    :return: str, the html table (cells are escaped by the inline renderer)
    """
    # a separator row only contains - : | and spaces
    is_sep = [bool(re.match(r'^[\s|:-]+$', row)) for row in rows]
    has_head = len(rows) > 1 and is_sep[1]
    html = ['<div class="table-wrap"><table class="md-table">']
    for it, row in enumerate(rows):
        if is_sep[it]:
            continue
        cells = [cell.strip() for cell in row.strip().strip('|').split('|')]
        tag = 'th' if has_head and it == 0 else 'td'
        # the inline markdown of the shared renderer (escapes html)
        html.append('<tr>' + ''.join('<{0}>{1}</{0}>'.format(
            tag, webapp.render_markdown(cell)[3:-4] if cell else '')
            for cell in cells) + '</tr>')
    html.append('</table></div>')
    return ''.join(html)


def _doc_ref(page: str, link: str) -> str:
    """
    Resolve a relative markdown link of a docs page to a page reference

    :param page: str, the reference of the page holding the link
    :param link: str, the link target (e.g. ../install or apero/)

    :return: str, the page reference (e.g. install)
    """
    link = link.strip()
    if link.endswith('.md'):
        link = link[:-3]
    # links are relative to the directory of the page
    parent = os.path.dirname(page)
    ref = os.path.normpath(os.path.join(parent, link)).strip('/')
    # only characters a token can hold
    return re.sub(r'[^\w./-]', '', ref)


def main(params: Any = None) -> None:
    """
    Start the APERO setup gui (blocks until stopped)

    :param params: ParamDict or None, the apero_setup command line
                   parameters (GUI_HOST / GUI_PORT / GUI_HEADLESS and any
                   setup values to fill in the form)

    :return: None
    """
    params = params if params is not None else dict()
    # setup values given on the command line pre-fill the form
    initial = dict()
    for name in commands.SARGS:
        if name.upper() in commands.SKIP_ARGS:
            continue
        # ParamDict keys (and their sources) are upper case
        sources = getattr(params, 'sources', dict())
        if sources.get(name.upper(), sources.get(name)) == 'command_line':
            initial[name] = params[name]
    skwargs = dict(host=str(params.get('GUI_HOST') or webapp.DEFAULT_HOST),
                   port=int(params.get('GUI_PORT') or 8099),
                   headless=bool(params.get('GUI_HEADLESS', False)),
                   worker_env=WORKER_ENV, title='APERO setup GUI')
    webapp.serve(lambda: SetupGuiApp(initial), **skwargs)


# =============================================================================
# End of code
# =============================================================================
