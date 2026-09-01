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
import json
import os
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
from apero.base import base as apero_base
from apero.tools.module.processing import drs_queue

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
# get the parameter dictionary
ParamDict = param_functions.ParamDict
# define the default host for the gui server (localhost only for safety)
GUI_DEFAULT_HOST = '127.0.0.1'
# define the default port for the gui server
GUI_DEFAULT_PORT = 8090
# define the number of ports to try if the default port is taken
GUI_PORT_ATTEMPTS = 50
# define the default number of rows per page in the status table
GUI_DEFAULT_ROWS = 25
# define the maximum number of entries for which we read the yaml files
#    to add detail columns (priority/recipe/runstring) to the table
#    (above this limit reading every yaml would be too slow - 600K+)
GUI_DETAIL_LIMIT = 10000
# define the maximum number of activity log messages kept in memory
GUI_MAX_MESSAGES = 200
# define the fields of the batch template shown in the settings panel
GUI_TEMPLATE_FIELDS = ['time', 'nodes', 'cpus_per_task', 'mem',
                       'account', 'job_name', 'mail_user', 'mail_type']
# define the directory that stores the queue gui static templates
GUI_DIR = os.path.join(os.path.dirname(__file__), 'gui')
# define the dashboard html template path
GUI_TEMPLATE_PATH = os.path.join(GUI_DIR, 'queue_template.html')


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


# define the dashboard html template (tokens XX_*_XX are replaced at
#    render time - we use tokens instead of str.format because the
#    css/js is full of curly braces)
GUI_HTML_TEMPLATE = _load_gui_html_template()


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
    for it, entry in enumerate(entries):
        # basic (listing only) information - always present
        row = dict()
        row['idx'] = it
        row['state'] = entry['state']
        row['group'] = entry['group']
        row['run'] = entry['run']
        # detail information (requires reading the yaml file)
        if details:
            try:
                run_dict = base.load_yaml(entry['path'])
                row['priority'] = run_dict.get('priority', '')
                row['recipe'] = run_dict.get('recipe', '')
                row['runstring'] = run_dict.get('runstring', '')
            except Exception as _:
                # unreadable yaml - leave the detail columns blank
                pass
        # add the row to the table data
        data.append(row)
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


def get_template_data(params: ParamDict) -> Dict[str, Any]:
    """
    Get the batch template as a plain (JSON-able) dictionary

    :param params: ParamDict, the parameter dictionary of constants

    :return: dictionary, the batch template values (defaults if no
             template file exists yet)
    """
    # get the template path
    queue_path = drs_queue.get_queue_path(params)
    template_path = os.path.join(queue_path,
                                 drs_queue.QUEUE_BATCH_TEMPLATE)
    # load the template (or the defaults if it doesn't exist)
    if os.path.exists(template_path):
        defaults = dict(drs_queue.QUEUE_BATCH_DEFAULTS)
        template = base.load_yaml(template_path, default=defaults)
    else:
        template = dict(drs_queue.QUEUE_BATCH_DEFAULTS)
    # return the template
    return dict(template)


def set_template_data(params: ParamDict,
                      form: Dict[str, Any]) -> Dict[str, Any]:
    """
    Save the batch template from a plain dictionary (e.g. a gui/flask
    form)

    :param params: ParamDict, the parameter dictionary of constants
    :param form: dictionary, the template values to save (only known
                 template keys are used)

    :return: dictionary, the saved template values
    """
    # make sure the queue directories exist
    drs_queue.setup_queue_directories(params)
    drs_queue.setup_output_directories(params)
    # start from the current template (or defaults)
    template = get_template_data(params)
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
    # save the template to the queue directory
    queue_path = drs_queue.get_queue_path(params)
    template_path = os.path.join(queue_path,
                                 drs_queue.QUEUE_BATCH_TEMPLATE)
    base.write_yaml(template, template_path, width=float('inf'))
    # return the saved template
    return template


def render_dashboard(params: ParamDict,
                     rows: int = GUI_DEFAULT_ROWS) -> str:
    """
    Render the queue dashboard html page

    :param params: ParamDict, the parameter dictionary of constants
    :param rows: int, the number of rows per page in the status table

    :return: str, the dashboard html
    """
    # fill the html template (tokens instead of format - css/js braces)
    html = GUI_HTML_TEMPLATE
    html = html.replace('XX_QPATH_XX',
                        drs_queue.get_queue_path(params))
    html = html.replace('XX_ROWS_XX', str(rows))
    html = html.replace('XX_TPLFIELDS_XX',
                        json.dumps(GUI_TEMPLATE_FIELDS))
    # return the rendered html
    return html


# =============================================================================
# Define action functions (reusable by flask / apero_ri)
# =============================================================================
def action_run(params: ParamDict, state: GuiState,
               cores: Optional[Any] = None,
               mpmode: Optional[str] = None) -> Dict[str, Any]:
    """
    Start a queue run action in the background (run the next task(s) in
    the queue - see drs_queue.queue_run)

    :param params: ParamDict, the parameter dictionary of constants
    :param state: GuiState, the shared gui state (busy flag/log)
    :param cores: int/str or None, the number of tasks to run at once
    :param mpmode: str or None, the multiprocessing mode

    :return: dictionary with keys 'started' (bool) and 'message' (str)
    """
    # sanitize the cores value
    try:
        cores = max(1, int(cores))
    except (TypeError, ValueError):
        cores = 1
    # sanitize the mpmode value
    if mpmode not in drs_queue.QUEUE_MP_MODES:
        mpmode = 'linear'

    # define the run action (executed in the worker thread)
    def _do_run():
        state.add_message('Run started (cores={0}, mpmode={1})'
                          ''.format(cores, mpmode))
        summary = drs_queue.queue_run(params, cores=cores,
                                      mpmode=mpmode)
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
                 submit: bool = False) -> Dict[str, Any]:
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

    :return: dictionary with keys 'started' (bool) and 'message' (str)
    """
    # sanitize the per_batch value (fall back to template cpus)
    try:
        per_batch = max(1, int(per_batch))
    except (TypeError, ValueError):
        template = get_template_data(params)
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

    # define the batch action (executed in the worker thread)
    def _do_batch():
        state.add_message('Batch started (per_batch={0}, n_batches={1},'
                          ' submit={2})'.format(per_batch, n_batches,
                                                submit))
        summary = drs_queue.batch_queue(params, per_batch, n_batches,
                                        submit)
        state.add_message('Batch: {0}'.format(summary['message']))
    # start the action in the background (if not busy)
    started = state.start_action('Batch', _do_batch, tuple())
    # construct the response
    if started:
        return dict(started=True, message='batch started')
    return dict(started=False, message='busy - action already running')


def action_reset(params: ParamDict, state: GuiState,
                 qstate: str = 'all') -> Dict[str, Any]:
    """
    Reset the queue (synchronous - reset is fast). Confirmation must be
    done by the caller (e.g. a browser confirm dialog)

    :param params: ParamDict, the parameter dictionary of constants
    :param state: GuiState, the shared gui state (busy flag/log)
    :param qstate: str, the queue state to reset ('all' or one of
                   pending/running/complete/failed)

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
    n_removed = drs_queue.reset_queue(params, states)
    # log the reset in the activity log
    message = 'Reset: removed {0} entries from {1}'
    message = message.format(n_removed, ', '.join(states))
    state.add_message(message)
    # construct the response
    return dict(removed=n_removed, message=message)


# =============================================================================
# Define server functions
# =============================================================================
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
            self.send_response(code)
            self.send_header('Content-Type',
                             '{0}; charset=utf-8'.format(ctype))
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

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
            # the gui state (busy flag + activity log)
            elif route == '/api/state':
                data = dict(busy=state.busy, messages=state.messages)
                self._send(json.dumps(data))
            # the batch template values
            elif route == '/api/template':
                self._send(json.dumps(get_template_data(params)))
            # unknown route
            else:
                self._send(json.dumps(dict(error='not found')),
                           code=404)

        # pylint: disable=invalid-name
        def do_POST(self):
            """Handle POST requests (actions)"""
            parsed = urlparse(self.path)
            route = parsed.path
            form = self._read_json()
            # run the next task(s)
            if route == '/api/run':
                response = action_run(params, state,
                                      cores=form.get('cores'),
                                      mpmode=form.get('mpmode'))
                self._send(json.dumps(response))
            # create (and optionally submit) batch scripts
            elif route == '/api/batch':
                response = action_batch(
                    params, state, per_batch=form.get('per_batch'),
                    n_batches=form.get('n_batches'),
                    submit=form.get('submit', False))
                self._send(json.dumps(response))
            # reset the queue
            elif route == '/api/reset':
                response = action_reset(params, state,
                                        qstate=form.get('qstate',
                                                        'all'))
                self._send(json.dumps(response))
            # save the batch template
            elif route == '/api/template':
                template = set_template_data(params, form)
                state.add_message('Batch template saved')
                self._send(json.dumps(template))
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
    # get the rows per page from user inputs (default 25)
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
        emsg = 'Queue: Could not find a free port (tried {0}-{1})'
        WLOG(params, 'error', emsg.format(port,
                                          port + GUI_PORT_ATTEMPTS))
        return
    # -------------------------------------------------------------------------
    # log where the dashboard is
    url = 'http://{0}:{1}/'.format(host, port)
    msg = 'Queue: Dashboard running at {0} (Ctrl+C to stop)'
    WLOG(params, 'info', msg.format(url))
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
        pass
    finally:
        server.server_close()
    # log that the server has stopped
    WLOG(params, '', 'Queue: Dashboard stopped')


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



