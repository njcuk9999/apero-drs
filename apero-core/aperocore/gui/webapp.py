#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generic browser gui application framework

Provides the reusable pieces of a small, dependency free (stdlib
http.server) browser gui:

    - GuiState: shared state (busy flag, activity messages per channel,
      data version counter)
    - read_log / job_tail: incremental and tail reading of log files
    - render_markdown: tiny markdown to html renderer for info pages
    - GuiApp: an application with GET/POST route tables, static file
      serving (shared core assets + application assets), the html page
      and the built-in api routes every gui gets (state, runtime info,
      processes, process logs, interactive jobs, file browsing, FITS
      viewing, diffs, batch templates, shutdown)
    - serve: start a GuiApp (optionally behind the recovery supervisor)

Applications subclass GuiApp, set their name/template/static directory and
add their own routes in add_routes(). All content functions return plain
(JSON-able) dictionaries so another server (e.g. flask) could reuse them.

Created on 2026-11-26

@author: cook
"""
import datetime
import getpass
import html as html_mod
import json
import mimetypes
import os
import re
import signal
import socket
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler
from http.server import ThreadingHTTPServer
from typing import Any, Callable, Dict, List, Optional, Tuple, Type
from urllib.parse import parse_qs, urlparse

from aperocore.gui import code_view
from aperocore.gui import diff as gui_diff
from aperocore.gui import files as gui_files
from aperocore.gui import fits_view
from aperocore.gui import jobs as gui_jobs
from aperocore.gui import mpl_view
from aperocore.gui import procs as gui_procs
from aperocore.gui import server as gui_server
from aperocore.gui import slurm as gui_slurm
from aperocore.gui import yaml_outline

# =============================================================================
# Define variables
# =============================================================================
# the size (css pixels) of the application icon in the top right corner
APP_ICON_SIZE = 36
__NAME__ = 'aperocore.gui.webapp.py'
# the directory holding the shared (core) static assets
CORE_STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')
# the shared css/js assets every page loads (in this order)
CORE_CSS = ['gui_base.css']
CORE_JS = ['gui_core.js', 'gui_console.js', 'gui_logviewer.js',
           'gui_processes.js', 'gui_files.js', 'gui_diff.js',
           'gui_params.js']
# default host (localhost only for safety) and port of the gui server
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 8095
# number of ports to try if the requested port is taken
PORT_ATTEMPTS = 50
# maximum number of activity messages kept per channel
MAX_MESSAGES = 200
# maximum number of log bytes sent in one response (first reads of large
#    logs only get the tail)
LOG_MAX_BYTES = 5 * 1024 * 1024
# regular expression for ANSI colour codes
ANSI_ESCAPE = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
# a request handler: takes a Request and returns a Response
Handler = Callable[['Request'], 'Response']


# =============================================================================
# Define classes
# =============================================================================
class GuiState:
    """
    Shared state for a gui server

    Holds the activity log messages (one list per channel, a channel is
    normally one page/tab of the gui) and a data version counter that is
    bumped whenever something changed on disk so browsers know to reload.
    """

    def __init__(self, channels: Optional[List[str]] = None) -> None:
        """
        Initialise the shared state

        :param channels: list of str or None, the activity log channels
                         (more are created on demand)

        :return: None
        """
        # all messages (most recent last) and the messages per channel
        self.messages: List[str] = []
        self.activity_messages: Dict[str, List[str]] = dict()
        for channel in channels or []:
            self.activity_messages[channel] = []
        # bumped whenever files the gui shows may have changed
        self.data_version = 0
        # lock protecting the state
        self.lock = threading.Lock()

    def add_message(self, message: str, channel: str = 'main') -> None:
        """
        Add a timestamped message to the activity log

        :param message: str, the message to add
        :param channel: str, the owning channel (page) of the message

        :return: None
        """
        with self.lock:
            # timestamp the message
            stamp = time.strftime('%H:%M:%S')
            entry = '[{0}] {1}'.format(stamp, message)
            # add to the global and the channel history (both bounded)
            self.messages.append(entry)
            del self.messages[:-MAX_MESSAGES]
            history = self.activity_messages.setdefault(channel, [])
            history.append(entry)
            del history[:-MAX_MESSAGES]

    def bump(self) -> None:
        """
        Tell browsers that data on disk changed (they reload)

        :return: None
        """
        with self.lock:
            self.data_version += 1


class Request:
    """
    One parsed http request (method, route, query and json body)
    """

    def __init__(self, method: str, raw_path: str, body: Any,
                 client: str) -> None:
        """
        Initialise the request

        :param method: str, 'GET' or 'POST'
        :param raw_path: str, the request path including the query string
        :param body: Any, the decoded json body (POST) or None
        :param client: str, the client address

        :return: None
        """
        parsed = urlparse(raw_path)
        self.method = method
        self.route = parsed.path
        self.query = parse_qs(parsed.query)
        self.body = body if isinstance(body, dict) else dict()
        self.client = client

    def arg(self, name: str, default: Any = None) -> Any:
        """
        Get a value from the json body (POST) or the query string (GET)

        :param name: str, the argument name
        :param default: Any, value returned if the argument is missing

        :return: Any, the argument value
        """
        if name in self.body:
            return self.body[name]
        if name in self.query:
            return self.query[name][0]
        return default

    def int_arg(self, name: str, default: int) -> int:
        """
        Get an integer argument (default if missing or not an integer)

        :param name: str, the argument name
        :param default: int, the default value

        :return: int, the argument value
        """
        try:
            return int(self.arg(name, default))
        except (TypeError, ValueError):
            return default


class Response:
    """
    One http response (status code, content type and body bytes)
    """

    def __init__(self, body: bytes, ctype: str = 'application/json',
                 code: int = 200,
                 headers: Optional[Dict[str, str]] = None) -> None:
        """
        Initialise the response

        :param body: bytes, the response body
        :param ctype: str, the content type
        :param code: int, the http status code
        :param headers: dict or None, extra headers

        :return: None
        """
        self.body = body
        self.ctype = ctype
        self.code = code
        self.headers = dict(headers or dict())

    @classmethod
    def json(cls, data: Any, code: int = 200) -> 'Response':
        """
        Build a json response

        :param data: Any, json serialisable data (str() for the rest)
        :param code: int, the http status code

        :return: Response, the response
        """
        text = json.dumps(data, default=str)
        return cls(text.encode('utf-8'), 'application/json; charset=utf-8',
                   code)

    @classmethod
    def html(cls, text: str, code: int = 200) -> 'Response':
        """
        Build an html response

        :param text: str, the html
        :param code: int, the http status code

        :return: Response, the response
        """
        return cls(text.encode('utf-8'), 'text/html; charset=utf-8', code)

    @classmethod
    def error(cls, message: str, code: int = 400) -> 'Response':
        """
        Build a json error response

        :param message: str, the error message
        :param code: int, the http status code

        :return: Response, the response
        """
        return cls.json(dict(error=str(message)), code)


# =============================================================================
# Define log functions
# =============================================================================
def empty_log(name: str = '') -> Dict[str, Any]:
    """
    Get an empty log response dictionary (see read_log)

    :param name: str, the id of the log (echoed back to the browser)

    :return: dict, the empty log response
    """
    return dict(qid=name, state=None, pid=None, pid_host=None, local=True,
                alive=False, exists=False, path='', size=0, start=0,
                offset=0, text='', truncated=False, reset=False,
                error=None)


def read_log(out: Dict[str, Any], log_path: str, offset: int,
             growing: bool, max_bytes: int = LOG_MAX_BYTES
             ) -> Dict[str, Any]:
    """
    Read (part of) a log file into a log response dictionary

    The log is read from byte "offset" onward. offset < 0 means a first
    read (only the last max_bytes are sent for large logs). While the log
    is still being written (growing) only complete lines are sent so the
    browser never receives half a line (or half an ANSI colour code).

    :param out: dict, the response dictionary to fill (see empty_log)
    :param log_path: str, the log file path
    :param offset: int, the byte offset to read from (-1 = first read)
    :param growing: bool, True while the log is still being written
    :param max_bytes: int, the maximum number of bytes to send

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
    # first read: only the tail of large logs
    if offset < 0:
        start = max(0, size - max_bytes)
        out['truncated'] = start > 0
    else:
        start = offset
    end = min(size, start + max_bytes)
    with open(log_path, 'rb') as logfile:
        logfile.seek(start)
        data = logfile.read(end - start)
    # a truncated first read starts at the next full line
    if out['truncated']:
        cut = data.find(b'\n')
        if cut >= 0:
            data = data[cut + 1:]
            start = start + cut + 1
    # while growing only send complete lines (the rest comes next poll)
    if growing:
        cut = data.rfind(b'\n')
        data = data[:cut + 1] if cut >= 0 else b''
    out['start'] = start
    out['offset'] = start + len(data)
    out['text'] = data.decode('utf-8', errors='replace')
    return out


def job_tail(path: str, nlines: int, keep_ansi: bool = False) -> List[str]:
    """
    Get the last lines of a log file (carriage returns become new lines
    so progress bars show their latest state)

    :param path: str, the log path
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
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    return text.splitlines()[-nlines:]


# =============================================================================
# Define markdown functions
# =============================================================================
def _markdown_inline(text: str) -> str:
    """
    Convert inline markdown (`code`, **bold** and [text](url)) of one line
    to html (the text is escaped first so it cannot inject html)

    :param text: str, one line of markdown text

    :return: str, the html for the line
    """
    text = html_mod.escape(text, quote=False)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\[([^\]]+)\]\((https?://[^)\s]+)\)',
                  r'<a href="\2" target="_blank">\1</a>', text)
    return text


def render_markdown(text: str) -> str:
    """
    Render simple markdown (headings, bullet lists, paragraphs, fenced
    code blocks, inline code, bold and links) to html

    :param text: str, the markdown text

    :return: str, the html
    """
    lines = text.splitlines()
    # collect html blocks; a block is a paragraph or a list item
    out: List[str] = []
    block: List[str] = []
    kind = 'p'
    in_list = False
    in_code = False
    # whether the previous line was blank (a non-indented line right after
    #   a list item continues it - as markdown "lazy" continuation lines)
    prev_blank = True

    def _flush() -> None:
        """
        Append the buffered paragraph or list item to the output

        :return: None
        """
        if not block:
            return
        para = _markdown_inline(' '.join(block))
        tag = 'li' if kind == 'li' else 'p'
        out.append('<{0}>{1}</{0}>'.format(tag, para))
        block.clear()

    for line in lines:
        stripped = line.strip()
        # fenced code blocks are copied verbatim (escaped)
        if stripped.startswith('```'):
            _flush()
            out.append('</code></pre>' if in_code else '<pre><code>')
            in_code = not in_code
            continue
        if in_code:
            out.append(html_mod.escape(line))
            continue
        heading = re.match(r'^(#{1,4})\s+(.*)$', stripped)
        is_item = stripped.startswith('- ')
        lazy = (in_list and kind == 'li' and bool(block) and not prev_blank)
        # blank lines, headings and new items end the current block
        if not stripped or heading or is_item:
            _flush()
        # leaving a list (anything except an item or its continuation)
        if in_list and (heading or (stripped and not is_item and not lazy
                                    and not line.startswith(' '))):
            # the item being read ends with the list
            _flush()
            out.append('</ul>')
            in_list = False
        prev_blank = not stripped
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
    if in_code:
        out.append('</code></pre>')
    return '\n'.join(out)


def render_markdown_file(path: str) -> str:
    """
    Render a markdown file to html (see render_markdown)

    :param path: str, the markdown file

    :return: str, the html (an error paragraph if the file is missing)
    """
    try:
        with open(path, 'r', encoding='utf-8') as mfile:
            return render_markdown(mfile.read())
    except OSError:
        return '<p>Missing info file: {0}</p>'.format(html_mod.escape(path))


# =============================================================================
# Define application icon functions
# =============================================================================
def app_icon_html(url: str, title: str) -> Dict[str, str]:
    """
    Get the html showing an application icon: a small icon fixed in the top
    right corner (above the global action buttons of the top bar) and the
    browser tab icon. Self contained (inline style) so any page template
    can use it.

    :param url: str, the url of the icon (e.g. static/app/icon.ico)
    :param title: str, the application name (icon tool tip)

    :return: dict(head, body) - head goes inside <head>, body anywhere in
             <body>
    """
    url = html_mod.escape(url, quote=True)
    title = html_mod.escape(title, quote=True)
    head = '<link rel="icon" href="{0}">'.format(url)
    body = ('<style>.gui-app-icon {{ position: fixed; top: 8px; '
            'right: 28px; width: {1}px; height: {1}px; z-index: 60; '
            'object-fit: contain; pointer-events: none; }} '
            '@media (max-width: 900px) {{ .gui-app-icon {{ display: none; '
            '}} }}</style><img class="gui-app-icon" src="{0}" alt="" '
            'title="{2}">'.format(url, APP_ICON_SIZE, title))
    return dict(head=head, body=body)


# =============================================================================
# Define the application class
# =============================================================================
class GuiApp:
    """
    A browser gui application (route tables + built-in api)

    Subclasses must set (class attributes or in __init__):

        - name: str, the application name (page title / brand)
        - template_path: str, the html page template (see render_page)
        - app_static_dir: str, directory of application static assets
        - icon_name: str (optional), an icon file in app_static_dir shown
          in the top right corner and as the browser tab icon
        - worker_env: str, environment variable for the supervisor worker
          port (unique per application)

    and should override:

        - state_dir(): directory for the process registry, job logs and
          batch templates (None while the gui has no working directory)
        - file_roots(): directories the file browser may access
        - add_routes(): register application routes with add_get/add_post
        - figure_roots(): directories pickled figures may be loaded from
          for interactive views (default none)
        - page_tokens(): extra XX_NAME_XX tokens for the page template
    """
    # the application name (page title / brand)
    name = 'GUI'
    # the html page template
    template_path = ''
    # directory of application static assets (served at /static/app/)
    app_static_dir = ''
    # an icon in app_static_dir (top right corner + browser tab icon)
    icon_name = ''
    # environment variable telling a supervised worker its private port
    worker_env = gui_server.WORKER_PORT_ENV
    # the activity log channels
    channels: List[str] = ['main']
    # the default batch template values (see aperocore.gui.slurm)
    batch_defaults: Dict[str, Any] = dict(gui_slurm.BATCH_DEFAULTS)

    def __init__(self) -> None:
        """
        Initialise the application (state, jobs and route tables)

        :return: None
        """
        # the shared state and the interactive/background job manager
        self.state = GuiState(self.channels)
        self.jobs = gui_jobs.JobManager(self.state, self.proc_dir,
                                        self.job_dir)
        # the route tables: route -> handler
        self.get_routes: Dict[str, Handler] = dict()
        self.post_routes: Dict[str, Handler] = dict()
        # information about this worker (captured once at start up)
        self.runtime_info = self.get_runtime_info()
        # register the built-in and the application routes
        self._add_core_routes()
        self.add_routes()

    # -------------------------------------------------------------------------
    # methods applications override
    # -------------------------------------------------------------------------
    def state_dir(self) -> Optional[str]:
        """
        Get the directory holding the gui state (process registry, job
        logs, batch templates) - None while no working directory is set

        :return: str or None, the state directory
        """
        return None

    def file_roots(self) -> List[str]:
        """
        Get the directories the file browser / viewers may access

        :return: list of str, absolute directories
        """
        return []

    def figure_roots(self) -> List[str]:
        """
        Get the directories pickled (interactive) figures may be loaded
        from (see aperocore.gui.mpl_view) - loading a pickle runs code so
        only folders the gui itself writes belong here

        :return: list of str, the directories (empty = no interactive
                 figures)
        """
        return []

    def add_routes(self) -> None:
        """
        Register the application routes (override in subclasses)

        :return: None
        """
        return None

    def page_tokens(self) -> Dict[str, str]:
        """
        Get extra XX_NAME_XX replacement tokens for the page template

        :return: dict, token name (without XX_ _XX) -> replacement text
        """
        return dict()

    def state_extra(self) -> Dict[str, Any]:
        """
        Get extra values added to the /api/state response

        :return: dict, extra state values
        """
        return dict()

    # -------------------------------------------------------------------------
    # directories
    # -------------------------------------------------------------------------
    def proc_dir(self) -> Optional[str]:
        """
        Get (and create) the process registry directory

        :return: str or None, the registry directory (None without a
                 state directory)
        """
        state_dir = self.state_dir()
        if state_dir is None:
            return None
        return gui_procs.get_proc_dir(state_dir)

    def job_dir(self) -> Optional[str]:
        """
        Get (and create) the gui job log directory

        :return: str or None, the job log directory (None without a
                 state directory)
        """
        state_dir = self.state_dir()
        if state_dir is None:
            return None
        path = os.path.join(state_dir, gui_procs.JOB_DIR_NAME)
        os.makedirs(path, exist_ok=True)
        return path

    def template_dir(self) -> Optional[str]:
        """
        Get the batch template directory

        :return: str or None, the template directory (None without a
                 state directory)
        """
        state_dir = self.state_dir()
        if state_dir is None:
            return None
        return os.path.join(state_dir, gui_slurm.TEMPLATE_DIR_NAME)

    # -------------------------------------------------------------------------
    # routes
    # -------------------------------------------------------------------------
    def add_get(self, route: str, handler: Handler) -> None:
        """
        Register a GET route

        :param route: str, the route (e.g. '/api/status')
        :param handler: callable, takes a Request returns a Response

        :return: None
        """
        self.get_routes[route] = handler

    def add_post(self, route: str, handler: Handler) -> None:
        """
        Register a POST route

        :param route: str, the route (e.g. '/api/run')
        :param handler: callable, takes a Request returns a Response

        :return: None
        """
        self.post_routes[route] = handler

    def handle(self, request: Request) -> Response:
        """
        Route one request to its handler

        :param request: Request, the request

        :return: Response, the response (404 for unknown routes)
        """
        # the page itself
        if request.method == 'GET' and request.route in ['/', '/index.html']:
            return Response.html(self.render_page())
        # static assets
        if request.method == 'GET' and request.route.startswith('/static/'):
            return self._static(request.route)
        # matplotlib toolbar icons (mpl.js loads them from _images/)
        if request.method == 'GET' and request.route.startswith('/_images/'):
            image = mpl_view.toolbar_image(request.route[len('/_images/'):])
            if image is None:
                return Response.error('not found', 404)
            return Response(image, 'image/png')
        # api routes
        table = self.get_routes if request.method == 'GET' else (
            self.post_routes)
        handler = table.get(request.route)
        if handler is None:
            return Response.error('not found', 404)
        return handler(request)

    def _static(self, route: str) -> Response:
        """
        Serve a static asset (/static/core/<file> or /static/app/<file>)

        :param route: str, the request route

        :return: Response, the asset (404 if unknown)
        """
        parts = route.split('/')
        # only plain file names are accepted (no sub-directories / ..)
        if len(parts) != 4 or parts[3] in ['', '.', '..']:
            return Response.error('not found', 404)
        if parts[2] == 'core':
            directory = CORE_STATIC_DIR
        elif parts[2] == 'app' and self.app_static_dir:
            directory = self.app_static_dir
        else:
            return Response.error('not found', 404)
        path = os.path.join(directory, parts[3])
        if not os.path.isfile(path):
            return Response.error('not found', 404)
        ctype = mimetypes.guess_type(path)[0] or 'application/octet-stream'
        if ctype.startswith('text/') or ctype.endswith('javascript'):
            ctype += '; charset=utf-8'
        with open(path, 'rb') as sfile:
            body = sfile.read()
        # re-read every time (editing assets only needs a page reload)
        return Response(body, ctype, headers={'Cache-Control': 'no-store'})

    def render_page(self) -> str:
        """
        Render the html page from the template

        Tokens replaced: XX_TITLE_XX, XX_CORE_HEAD_XX (the shared css/js
        tags), XX_CORE_BODY_XX (the shared dialogs) and every token from
        page_tokens(). Tokens are used instead of str.format because the
        page contains css/js braces.

        :return: str, the page html
        """
        try:
            with open(self.template_path, 'r', encoding='utf-8') as hfile:
                page = hfile.read()
        except OSError:
            return ('<!DOCTYPE html><html><body><h1>{0}</h1><p>Missing gui '
                    'template: {1}</p></body></html>'
                    ''.format(html_mod.escape(self.name),
                              html_mod.escape(self.template_path)))
        # the shared assets (a time stamp defeats browser caching)
        stamp = str(int(time.time()))
        head = []
        for name in CORE_CSS:
            head.append('<link rel="stylesheet" href="static/core/{0}?v={1}">'
                        ''.format(name, stamp))
        for name in CORE_JS:
            head.append('<script src="static/core/{0}?v={1}"></script>'
                        ''.format(name, stamp))
        # the shared dialogs (log viewer, file picker, viewers, diff)
        body_path = os.path.join(CORE_STATIC_DIR, 'gui_body.html')
        with open(body_path, 'r', encoding='utf-8') as bfile:
            body = bfile.read()
        # the application icon (if there is one)
        if self.icon_name and self.app_static_dir and os.path.isfile(
                os.path.join(self.app_static_dir, self.icon_name)):
            icon = app_icon_html('static/app/{0}?v={1}'.format(
                self.icon_name, stamp), self.name)
            head.append(icon['head'])
            body += icon['body']
        tokens = dict(TITLE=html_mod.escape(self.name),
                      CORE_HEAD='\n'.join(head), CORE_BODY=body,
                      STAMP=stamp)
        tokens.update(self.page_tokens())
        for key, value in tokens.items():
            page = page.replace('XX_{0}_XX'.format(key), str(value))
        return page

    # -------------------------------------------------------------------------
    # built-in routes
    # -------------------------------------------------------------------------
    def _add_core_routes(self) -> None:
        """
        Register the built-in api routes every gui gets

        :return: None
        """
        # state, runtime info and shutdown
        self.add_get('/api/state', self.api_state)
        self.add_get('/api/runtime_info',
                     lambda req: Response.json(self.runtime_info))
        # processes (registry) and their logs
        self.add_get('/api/processes', self.api_processes)
        self.add_get('/api/process_log', self.api_process_log)
        self.add_post('/api/process', self.api_process)
        self.add_get('/api/slurm',
                     lambda req: Response.json(
                         gui_procs.slurm_job_details()))
        # interactive / background jobs (the consoles)
        self.add_get('/api/job', self.api_job)
        self.add_post('/api/job_input', self.api_job_input)
        self.add_post('/api/job_stop', self.api_job_stop)
        # file browsing and viewers
        self.add_get('/api/fs/roots', self.api_fs_roots)
        self.add_get('/api/fs/list', self.api_fs_list)
        self.add_get('/api/fs/raw', self.api_fs_raw)
        self.add_get('/api/fs/text', self.api_fs_text)
        self.add_post('/api/fs/delete', self.api_fs_delete)
        self.add_get('/api/fits/info', self.api_fits_info)
        self.add_get('/api/fits/image', self.api_fits_image)
        self.add_get('/api/fits/table', self.api_fits_table)
        # interactive matplotlib figures (matplotlib's own toolbar)
        self.add_post('/api/figure/open', self.api_figure_open)
        self.add_post('/api/figure/send', self.api_figure_send)
        self.add_get('/api/figure/poll', self.api_figure_poll)
        self.add_post('/api/figure/close', self.api_figure_close)
        self.add_get('/api/figure/mpl.js', self.api_figure_asset)
        self.add_get('/api/figure/mpl.css', self.api_figure_asset)
        # python source code (read only)
        self.add_get('/api/code', self.api_code)
        # diffs and yaml outlines
        self.add_post('/api/diff', self.api_diff)
        self.add_post('/api/yaml/outline', self.api_yaml_outline)
        self.add_post('/api/yaml/apply', self.api_yaml_apply)
        self.add_post('/api/yaml/add', self.api_yaml_add)
        self.add_post('/api/yaml/remove', self.api_yaml_remove)
        # batch templates
        self.add_get('/api/templates', self.api_templates)
        self.add_get('/api/template', self.api_template)
        self.add_post('/api/template', self.api_template_save)
        # shutdown is handled by the http handler (needs the server)

    def api_state(self, request: Request) -> Response:
        """
        GET /api/state: activity messages, data version and running jobs

        :param request: Request, the request

        :return: Response, json state
        """
        _ = request
        data = dict(messages=list(self.state.messages),
                    activity_messages=dict(self.state.activity_messages),
                    data_version=self.state.data_version,
                    jobs=self.jobs.summary(),
                    sbatch=gui_slurm.sbatch_available())
        data.update(self.state_extra())
        return Response.json(data)

    def api_processes(self, request: Request) -> Response:
        """
        GET /api/processes: the registered processes with live status

        :param request: Request, the request

        :return: Response, json dict(processes, slurm, host)
        """
        _ = request
        proc_dir = self.proc_dir()
        if proc_dir is None:
            return Response.json(dict(processes=[], slurm=False,
                                      host=socket.gethostname()))
        return Response.json(get_process_data(proc_dir))

    def api_process_log(self, request: Request) -> Response:
        """
        GET /api/process_log?id=&file=&offset=: one log of a process

        :param request: Request, the request

        :return: Response, json log response (see read_log)
        """
        proc_dir = self.proc_dir()
        proc_id = str(request.arg('id', ''))
        index = request.int_arg('file', 0)
        offset = request.int_arg('offset', -1)
        if proc_dir is None:
            out = empty_log(proc_id)
            out['error'] = 'no working directory set'
            return Response.json(out)
        return Response.json(get_process_log(proc_dir, proc_id, index,
                                             offset))

    def api_process(self, request: Request) -> Response:
        """
        POST /api/process {op, ids}: stop / remove / clear processes

        :param request: Request, the request

        :return: Response, json dict(success, message)
        """
        proc_dir = self.proc_dir()
        if proc_dir is None:
            return Response.error('no working directory set')
        ids = request.arg('ids', []) or []
        if not isinstance(ids, list):
            ids = []
        result = action_process(proc_dir, str(request.arg('op', '')),
                                [str(pid) for pid in ids],
                                artifact_roots=self.artifact_roots())
        self.state.add_message(result['message'], 'processes')
        self.state.bump()
        return Response.json(result)

    def artifact_roots(self) -> List[str]:
        """
        Get the directories whose files belong to the gui (deleted with
        their process records) - override to add e.g. batch script dirs

        :return: list of str, the directories
        """
        return []

    def api_job(self, request: Request) -> Response:
        """
        GET /api/job?channel=: the current/last job of a channel (with
        the tail of its output)

        :param request: Request, the request

        :return: Response, json job dict (empty if no job ran yet)
        """
        channel = str(request.arg('channel', 'main'))
        return Response.json(self.jobs.get(channel))

    def api_job_input(self, request: Request) -> Response:
        """
        POST /api/job_input {channel, text}: send a line to a running
        interactive job

        :param request: Request, the request

        :return: Response, json dict(success, message)
        """
        channel = str(request.arg('channel', 'main'))
        text = str(request.arg('text', ''))
        return Response.json(self.jobs.send_input(channel, text))

    def api_job_stop(self, request: Request) -> Response:
        """
        POST /api/job_stop {channel}: stop the running job of a channel

        :param request: Request, the request

        :return: Response, json dict(success, message)
        """
        channel = str(request.arg('channel', 'main'))
        return Response.json(self.jobs.stop(channel))

    def api_fs_roots(self, request: Request) -> Response:
        """
        GET /api/fs/roots: the directories the file browser may access

        :param request: Request, the request

        :return: Response, json dict(roots, home)
        """
        _ = request
        return Response.json(dict(roots=self.file_roots(),
                                  home=os.path.expanduser('~')))

    def _browse_roots(self, request: Request) -> Optional[List[str]]:
        """
        Get the roots for a file browser request: the application roots,
        or no restriction (None) when the browser asks for "any" (used by
        the open-file dialog - read only)

        :param request: Request, the request

        :return: list of str or None, the allowed roots
        """
        if str(request.arg('any', '')).lower() in ['1', 'true']:
            return None
        return self.file_roots()

    def api_fs_list(self, request: Request) -> Response:
        """
        GET /api/fs/list?path=&any=&ext=: list one directory

        :param request: Request, the request

        :return: Response, json listing (see files.list_directory)
        """
        path = str(request.arg('path', '') or '')
        exts = [ext for ext in str(request.arg('ext', '')).split(',')
                if ext]
        try:
            data = gui_files.list_directory(path, self._browse_roots(request),
                                            exts=exts)
        except gui_files.FileAccessError as error:
            return Response.error(str(error), 403)
        return Response.json(data)

    def api_fs_raw(self, request: Request) -> Response:
        """
        GET /api/fs/raw?path=: the raw bytes of a file (images, downloads)

        :param request: Request, the request

        :return: Response, the file content
        """
        path = str(request.arg('path', ''))
        try:
            real = gui_files.check_path(path, self.file_roots())
        except gui_files.FileAccessError as error:
            return Response.error(str(error), 403)
        if not os.path.isfile(real):
            return Response.error('not a file', 404)
        ctype = mimetypes.guess_type(real)[0] or 'application/octet-stream'
        headers = dict()
        if str(request.arg('download', '')).lower() in ['1', 'true']:
            disp = 'attachment; filename="{0}"'.format(
                os.path.basename(real).replace('"', ''))
            headers['Content-Disposition'] = disp
        with open(real, 'rb') as rfile:
            body = rfile.read()
        return Response(body, ctype, headers=headers)

    def api_fs_text(self, request: Request) -> Response:
        """
        GET /api/fs/text?path=&any=: the text of a (small) text file

        :param request: Request, the request

        :return: Response, json dict(path, text, truncated, size)
        """
        path = str(request.arg('path', ''))
        try:
            data = gui_files.read_text(path, self._browse_roots(request))
        except gui_files.FileAccessError as error:
            return Response.error(str(error), 403)
        return Response.json(data)

    def api_fs_delete(self, request: Request) -> Response:
        """
        POST /api/fs/delete {paths}: delete files/directories (only inside
        the application roots, never a root itself)

        :param request: Request, the request

        :return: Response, json dict(success, message, deleted)
        """
        paths = request.arg('paths', []) or []
        if not isinstance(paths, list):
            paths = [paths]
        result = gui_files.delete_paths([str(p) for p in paths],
                                        self.file_roots())
        self.state.add_message(result['message'], 'files')
        self.state.bump()
        return Response.json(result)

    def api_fits_info(self, request: Request) -> Response:
        """
        GET /api/fits/info?path=: the HDU list and headers of a FITS file

        :param request: Request, the request

        :return: Response, json (see fits_view.fits_info)
        """
        try:
            real = gui_files.check_path(str(request.arg('path', '')),
                                        self.file_roots())
        except gui_files.FileAccessError as error:
            return Response.error(str(error), 403)
        return Response.json(fits_view.fits_info(real))

    def api_fits_image(self, request: Request) -> Response:
        """
        GET /api/fits/image?path=&hdu=&plane=&scale=&cmap=: png preview of
        an image extension

        :param request: Request, the request

        :return: Response, the png image (json error if not possible)
        """
        try:
            real = gui_files.check_path(str(request.arg('path', '')),
                                        self.file_roots())
        except gui_files.FileAccessError as error:
            return Response.error(str(error), 403)
        fkwargs = dict(hdu=request.int_arg('hdu', 0),
                       plane=request.int_arg('plane', 0),
                       scale=str(request.arg('scale', 'zscale')),
                       cmap=str(request.arg('cmap', 'gray')))
        try:
            png = fits_view.image_png(real, **fkwargs)
        except fits_view.FitsViewError as error:
            return Response.error(str(error))
        return Response(png, 'image/png')

    def api_figure_open(self, request: Request) -> Response:
        """
        POST /api/figure/open {path}: open a pickled figure in
        matplotlib's browser backend (see mpl_view)

        :param request: Request, the request

        :return: Response, json dict(id, title, warning)
        """
        try:
            data = mpl_view.open_figure(str(request.arg('path', '')),
                                        self.figure_roots())
        except mpl_view.FigureViewError as error:
            return Response.error(str(error))
        return Response.json(data)

    def api_figure_send(self, request: Request) -> Response:
        """
        POST /api/figure/send {id, messages}: browser events for an open
        figure (mouse, keys, toolbar, draw requests from mpl.js)

        :param request: Request, the request

        :return: Response, json dict(success)
        """
        messages = request.arg('messages', []) or []
        if not isinstance(messages, list):
            messages = [messages]
        try:
            session = mpl_view.get_session(str(request.arg('id', '')))
        except mpl_view.FigureViewError as error:
            return Response.error(str(error), 410)
        session.handle(messages)
        return Response.json(dict(success=True))

    def api_figure_poll(self, request: Request) -> Response:
        """
        GET /api/figure/poll?id=&wait=: the messages / images matplotlib
        sent for an open figure (waits up to wait seconds for one)

        :param request: Request, the request

        :return: Response, json dict(messages)
        """
        try:
            session = mpl_view.get_session(str(request.arg('id', '')))
        except mpl_view.FigureViewError as error:
            return Response.error(str(error), 410)
        wait = float(max(0, request.int_arg('wait', 10)))
        return Response.json(dict(messages=session.poll(wait)))

    def api_figure_close(self, request: Request) -> Response:
        """
        POST /api/figure/close {id}: close an open figure

        :param request: Request, the request

        :return: Response, json dict(success)
        """
        mpl_view.close_figure(str(request.arg('id', '')))
        return Response.json(dict(success=True))

    def api_figure_asset(self, request: Request) -> Response:
        """
        GET /api/figure/mpl.js or /api/figure/mpl.css: matplotlib's
        browser figure code / styles

        :param request: Request, the request

        :return: Response, the javascript or css
        """
        if request.route.endswith('.css'):
            return Response(mpl_view.stylesheet().encode('utf-8'),
                            'text/css; charset=utf-8')
        return Response(mpl_view.javascript().encode('utf-8'),
                        'application/javascript; charset=utf-8')

    def api_fits_table(self, request: Request) -> Response:
        """
        GET /api/fits/table?path=&hdu=&start=&rows=: rows of a table
        extension

        :param request: Request, the request

        :return: Response, json (see fits_view.table_rows)
        """
        try:
            real = gui_files.check_path(str(request.arg('path', '')),
                                        self.file_roots())
        except gui_files.FileAccessError as error:
            return Response.error(str(error), 403)
        fkwargs = dict(hdu=request.int_arg('hdu', 1),
                       start=request.int_arg('start', 0),
                       nrows=request.int_arg('rows', 100))
        try:
            data = fits_view.table_rows(real, **fkwargs)
        except fits_view.FitsViewError as error:
            return Response.error(str(error))
        return Response.json(data)

    def api_diff(self, request: Request) -> Response:
        """
        POST /api/diff: side by side diff of two files ({left, right}
        paths, "any" to allow files outside the roots) or two texts
        ({left_text, right_text})

        :param request: Request, the request

        :return: Response, json (see diff.side_by_side)
        """
        names = []
        texts = []
        for side in ['left', 'right']:
            text = request.arg(side + '_text', None)
            if text is not None:
                texts.append(str(text))
                names.append(str(request.arg(side + '_name', side)))
                continue
            path = str(request.arg(side, '') or '')
            try:
                data = gui_files.read_text(path, self._browse_roots(request),
                                           max_bytes=20 * 1024 * 1024)
            except gui_files.FileAccessError as error:
                return Response.error(str(error), 403)
            if data.get('error'):
                return Response.error('{0}: {1}'.format(path, data['error']))
            texts.append(data['text'])
            names.append(data['path'])
        context = request.int_arg('context', -1)
        result = gui_diff.side_by_side(texts[0], texts[1],
                                       context=None if context < 0
                                       else context)
        result['left_name'], result['right_name'] = names
        return Response.json(result)

    def api_yaml_outline(self, request: Request) -> Response:
        """
        POST /api/yaml/outline {text}: the editable outline of yaml text

        :param request: Request, the request

        :return: Response, json (see yaml_outline.outline)
        """
        text = str(request.arg('text', ''))
        return Response.json(yaml_outline.outline(text))

    def api_code(self, request: Request) -> Response:
        """
        GET /api/code?func=pkg.module.func or ?file=&line=: the source of
        a function (with its docstring) or the code block starting at a
        line - read only, .py files on the python path only

        :param request: Request, the request

        :return: Response, json (see aperocore.gui.code_view)
        """
        func = str(request.arg('func', '') or '')
        if func:
            return Response.json(code_view.find_function(func))
        path = str(request.arg('file', '') or '')
        if not path:
            return Response.error('give func or file')
        return Response.json(code_view.read_block(
            path, request.int_arg('line', 1)))

    def api_yaml_apply(self, request: Request) -> Response:
        """
        POST /api/yaml/apply {text, edits}: apply value edits to yaml text
        (comments and layout preserved)

        :param request: Request, the request

        :return: Response, json dict(text, errors)
        """
        text = str(request.arg('text', ''))
        edits = request.arg('edits', []) or []
        if not isinstance(edits, list):
            edits = []
        return Response.json(yaml_outline.apply_edits(text, edits))

    def api_yaml_add(self, request: Request) -> Response:
        """
        POST /api/yaml/add {text, entries}: add new keys to yaml text (only
        new lines are inserted - nothing is written to disk)

        :param request: Request, the request

        :return: Response, json dict(text, added, errors)
        """
        text = str(request.arg('text', ''))
        entries = request.arg('entries', []) or []
        if not isinstance(entries, list):
            entries = []
        return Response.json(yaml_outline.add_entries(text, entries))

    def api_yaml_remove(self, request: Request) -> Response:
        """
        POST /api/yaml/remove {text, keys}: remove keys from yaml text (only
        their lines are taken out - nothing is written to disk)

        :param request: Request, the request

        :return: Response, json dict(text, removed, errors)
        """
        text = str(request.arg('text', ''))
        keys = request.arg('keys', []) or []
        if not isinstance(keys, list):
            keys = []
        return Response.json(yaml_outline.remove_entries(text, keys))

    def api_templates(self, request: Request) -> Response:
        """
        GET /api/templates: the saved batch template names

        :param request: Request, the request

        :return: Response, json dict(names, fields, sbatch)
        """
        _ = request
        template_dir = self.template_dir()
        names = [] if template_dir is None else (
            gui_slurm.list_templates(template_dir))
        return Response.json(dict(names=names,
                                  fields=gui_slurm.TEMPLATE_FIELDS,
                                  sbatch=gui_slurm.sbatch_available()))

    def api_template(self, request: Request) -> Response:
        """
        GET /api/template?name=: one batch template (defaults if unsaved)

        :param request: Request, the request

        :return: Response, json template dict
        """
        template_dir = self.template_dir()
        name = request.arg('name', None)
        if template_dir is None:
            return Response.json(dict(self.batch_defaults))
        return Response.json(gui_slurm.load_template(
            template_dir, name, self.batch_defaults))

    def api_template_save(self, request: Request) -> Response:
        """
        POST /api/template {name, fields..., activation}: save a template

        :param request: Request, the request

        :return: Response, json dict(template, path, message)
        """
        template_dir = self.template_dir()
        if template_dir is None:
            return Response.error('no working directory set')
        name = gui_slurm.sanitize_template_name(request.arg('name', None))
        skwargs = dict(defaults=self.batch_defaults)
        template, path = gui_slurm.update_template(template_dir, name,
                                                   request.body, **skwargs)
        message = 'Batch template "{0}" saved to {1}'.format(name, path)
        self.state.add_message(message, 'run')
        return Response.json(dict(template=template, path=path,
                                  message=message))

    # -------------------------------------------------------------------------
    # runtime information
    # -------------------------------------------------------------------------
    def get_runtime_info(self) -> Dict[str, Any]:
        """
        Capture information about this gui worker at start up

        :return: dict, json serialisable worker information
        """
        info: Dict[str, Any] = dict()
        info['name'] = self.name
        info['user'] = getpass.getuser()
        info['hostname'] = socket.gethostname()
        info['pid'] = os.getpid()
        info['started'] = datetime.datetime.now(
            datetime.timezone.utc).isoformat()
        info['python'] = sys.version.split()[0]
        info['python_executable'] = sys.executable
        return info


# =============================================================================
# Define process content functions
# =============================================================================
def get_process_data(proc_dir: str) -> Dict[str, Any]:
    """
    Get the registered processes with their live status

    :param proc_dir: str, the registry directory

    :return: dict(processes=list of dicts, slurm=bool, host=str)
    """
    records = gui_procs.load_all(proc_dir)
    # one squeue call for every unfinished slurm job
    jobs = [job for rec in records if not rec.get('finished')
            for job in rec.get('slurm_jobs') or []]
    slurm = gui_procs.slurm_states(jobs)
    rows = []
    for record in records:
        row = dict(record)
        row['status'] = gui_procs.proc_status(record, slurm)
        row['logs'] = [os.path.basename(path)
                       for path in gui_procs.log_files(record)]
        row['n_qids'] = len(record.get('qids') or [])
        row.pop('qids', None)
        rows.append(row)
    return dict(processes=rows, slurm=slurm is not None,
                host=socket.gethostname())


def get_process_log(proc_dir: str, proc_id: str, index: int = 0,
                    offset: int = -1) -> Dict[str, Any]:
    """
    Get (part of) one log file of a registered process

    :param proc_dir: str, the registry directory
    :param proc_id: str, the process id
    :param index: int, which of the process log files to read
    :param offset: int, the byte offset to read from (-1 = first read)

    :return: dict, see read_log
    """
    out = empty_log(proc_id)
    record = gui_procs.load(proc_dir, proc_id)
    if record is None:
        out['error'] = 'unknown process'
        return out
    jobs = record.get('slurm_jobs') or []
    status = gui_procs.proc_status(record, gui_procs.slurm_states(jobs))
    growing = status in ['running', 'pending', 'unknown']
    # map onto the log viewer states (running keeps it polling)
    if growing:
        out['state'] = 'running'
    elif status in ['complete', 'finished']:
        out['state'] = 'complete'
    else:
        out['state'] = 'failed'
    out['pid'] = record.get('pid')
    out['pid_host'] = record.get('host')
    out['local'] = record.get('host') == socket.gethostname()
    out['alive'] = status == 'running'
    paths = gui_procs.log_files(record)
    if not 0 <= index < len(paths):
        out['path'] = '(no log file yet)'
        return out
    return read_log(out, paths[index], offset, growing)


def action_process(proc_dir: str, op: str, ids: List[str],
                   artifact_roots: Optional[List[str]] = None
                   ) -> Dict[str, Any]:
    """
    Stop processes or tidy the process list

    :param proc_dir: str, the registry directory
    :param op: str, 'stop' (ids), 'remove' (ids), 'clear_finished' or
               'clear_all' (every inactive record)
    :param ids: list of str, the process ids (stop/remove)
    :param artifact_roots: list of str or None, directories whose files
                           belong to the gui (deleted with the records)

    :return: dict(success, message)
    """
    if op == 'stop':
        messages, success = [], True
        for proc_id in ids:
            record = gui_procs.load(proc_dir, proc_id)
            if record is None:
                messages.append('unknown process {0}'.format(proc_id))
                success = False
                continue
            result = gui_procs.stop_process(proc_dir, record)
            success = success and result['success']
            messages.append(result['message'])
        return dict(success=success, message='\n'.join(messages))
    if op in ['remove', 'clear_finished', 'clear_all']:
        if op == 'remove':
            targets = list(ids)
        else:
            data = get_process_data(proc_dir)['processes']
            active = ['running', 'pending', 'unknown']
            targets = [row['id'] for row in data
                       if op == 'clear_all' or row['status'] not in active]
        # gui owned artifacts (e.g. sbatch scripts) only go with no
        #    remaining record sharing them (protected list given)
        rargs = [proc_dir, targets, artifact_roots or [], []]
        removed = gui_procs.remove(*rargs)
        message = 'Removed {0} process record(s){1}'.format(
            removed, '' if removed == len(set(targets)) else
            ' ({0} still active - stop them first)'.format(
                len(set(targets)) - removed))
        return dict(success=removed == len(set(targets)), message=message)
    return dict(success=False, message='unknown process action: ' + str(op))


# =============================================================================
# Define server functions
# =============================================================================
def make_handler(app: GuiApp) -> Type[BaseHTTPRequestHandler]:
    """
    Create the http request handler class for a gui application

    :param app: GuiApp, the application the handler routes requests to

    :return: the request handler class
    """

    class GuiHandler(BaseHTTPRequestHandler):
        """Request handler routing every request to the application"""

        def log_message(self, fmt: str, *args: Any) -> None:
            """
            Suppress the default per-request log output

            :param fmt: str, the log format
            :param args: the log values

            :return: None
            """
            _ = fmt, args

        def _send(self, response: Response) -> None:
            """
            Send a response (tolerating a client closing the connection)

            :param response: Response, the response to send

            :return: None
            """
            try:
                self.send_response(response.code)
                self.send_header('Content-Type', response.ctype)
                self.send_header('Content-Length', str(len(response.body)))
                for key, value in response.headers.items():
                    self.send_header(key, value)
                self.end_headers()
                self.wfile.write(response.body)
            except (BrokenPipeError, ConnectionResetError):
                pass

        def _body(self) -> Any:
            """
            Read the request body as json (empty dict if missing/invalid)

            :return: Any, the decoded body
            """
            try:
                length = int(self.headers.get('Content-Length', 0))
                if length == 0:
                    return dict()
                return json.loads(self.rfile.read(length))
            except (ValueError, TypeError):
                return dict()

        def _dispatch(self, method: str) -> None:
            """
            Route one request (errors become json 500 responses)

            :param method: str, 'GET' or 'POST'

            :return: None
            """
            body = self._body() if method == 'POST' else None
            request = Request(method, self.path, body,
                              self.client_address[0])
            # shutdown needs the server (run in a thread: shutdown blocks
            #   until the current request is finished)
            if method == 'POST' and request.route == '/api/shutdown':
                self._send(Response.json(dict(message='shutting down')))
                threading.Thread(target=self.server.shutdown,
                                 daemon=True).start()
                return
            try:
                response = app.handle(request)
            except Exception as gui_error:
                emsg = '{0}: {1}'.format(type(gui_error).__name__,
                                         gui_error)
                sys.stderr.write('GUI request {0} failed: {1}\n'.format(
                    self.path, emsg))
                response = Response.error(emsg, 500)
            self._send(response)

        # pylint: disable=invalid-name
        def do_GET(self) -> None:
            """
            Handle GET requests

            :return: None
            """
            self._dispatch('GET')

        # pylint: disable=invalid-name
        def do_POST(self) -> None:
            """
            Handle POST requests

            :return: None
            """
            self._dispatch('POST')

    return GuiHandler


def serve(app_factory: Callable[[], GuiApp], host: str = DEFAULT_HOST,
          port: int = DEFAULT_PORT, headless: bool = False,
          worker_env: str = gui_server.WORKER_PORT_ENV,
          title: str = 'GUI',
          log: Optional[Callable[[str], None]] = None) -> None:
    """
    Start a gui application server and (optionally) open it in a browser

    The first call starts the supervisor (SupervisorServer) on the public
    host/port which re-runs this same command as the worker process with
    worker_env set to a private port; in the worker this function builds
    the application and serves it on that private port. The supervisor
    lets the gui "Restart server" button replace a hung worker without
    the url changing.

    :param app_factory: callable returning the GuiApp (only called in the
                        worker so the supervisor stays light)
    :param host: str, the public host to listen on
    :param port: int, the first public port to try
    :param headless: bool, if True do not open a browser
    :param worker_env: str, environment variable for the worker port
    :param title: str, the application name (recovery page / logs)
    :param log: callable or None, prints messages for the user (default:
                print, flushed so it shows up when output is redirected)

    :return: None
    """
    if log is None:
        def log(message: str) -> None:
            """
            Print a message immediately

            :param message: str, the message

            :return: None
            """
            print(message, flush=True)
    worker_port = os.environ.get(worker_env)
    # -------------------------------------------------------------------------
    # worker: serve the application on the private port
    if worker_port is not None:
        app = app_factory()
        server = ThreadingHTTPServer((DEFAULT_HOST, int(worker_port)),
                                     make_handler(app))
        # stop when the supervisor disappears (e.g. killed) - no orphans
        _watch_parent(server)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
            app.jobs.shutdown()
        return
    # -------------------------------------------------------------------------
    # supervisor: find a free public port and start the worker
    supervisor = None
    command = [sys.executable] + sys.orig_argv[1:]
    skwargs = dict(worker_env=worker_env, title=title)
    for p_it in range(PORT_ATTEMPTS):
        try:
            address = (host, port + p_it)
            supervisor = gui_server.SupervisorServer(address, command,
                                                     **skwargs)
            port = port + p_it
            break
        except OSError:
            continue
    if supervisor is None:
        log('{0}: could not find a free port (tried {1}-{2})'.format(
            title, port, port + PORT_ATTEMPTS))
        return
    supervisor.start_worker()
    # a SIGTERM (kill, timeout, batch systems) stops cleanly like Ctrl+C
    signal.signal(signal.SIGTERM, _raise_interrupt)
    # -------------------------------------------------------------------------
    # tell the user where the gui is (and open a browser)
    url = 'http://{0}:{1}/'.format(host, port)
    log('{0} running at: {1}  (Ctrl+C to stop)'.format(title, url))
    if host in ['127.0.0.1', 'localhost']:
        log('From another machine use an ssh tunnel e.g. '
            'ssh -N -L {0}:localhost:{0} {1}@{2}'.format(
                port, getpass.getuser(), socket.gethostname()))
    if not headless:
        try:
            import webbrowser
            webbrowser.open(url)
        except Exception as _:
            pass
    # -------------------------------------------------------------------------
    # serve until Ctrl+C or the gui Shutdown button
    try:
        supervisor.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        supervisor.server_close()
        supervisor.finish_worker()
    log('{0} stopped'.format(title))


def _raise_interrupt(signum: int, frame: Any) -> None:
    """
    Signal handler turning SIGTERM into KeyboardInterrupt (so the
    supervisor stops its worker on the way out)

    :param signum: int, the signal number
    :param frame: the current stack frame

    :raises KeyboardInterrupt: always

    :return: None
    """
    _ = signum, frame
    raise KeyboardInterrupt()


def _watch_parent(server: ThreadingHTTPServer,
                  interval: float = 2.0) -> None:
    """
    Shut a worker server down when its parent (the supervisor) exits

    :param server: ThreadingHTTPServer, the worker server
    :param interval: float, seconds between checks

    :return: None
    """
    parent = os.getppid()

    def _watch() -> None:
        """
        Poll the parent pid (re-parented = the supervisor died)

        :return: None
        """
        while True:
            time.sleep(interval)
            if os.getppid() != parent:
                server.shutdown()
                return

    threading.Thread(target=_watch, daemon=True).start()


def find_free_port(host: str, port: int) -> Tuple[str, int]:
    """
    Find the first free port at or after "port" (helper for tests)

    :param host: str, the host
    :param port: int, the first port to try

    :return: tuple, (host, free port)
    """
    for p_it in range(PORT_ATTEMPTS):
        with socket.socket() as probe:
            try:
                probe.bind((host, port + p_it))
            except OSError:
                continue
            return host, port + p_it
    raise OSError('no free port found')


# =============================================================================
# End of code
# =============================================================================
