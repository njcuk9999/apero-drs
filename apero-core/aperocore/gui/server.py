#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generic supervisor for browser gui servers

Keeps gui recovery independent of the gui worker process: a small public
http server (SupervisorServer) listens on the public port and proxies every
request to a disposable worker process (the actual gui) listening on a
private loopback port. If the worker hangs or crashes the supervisor can
restart it (the "restart" request) without the public url changing.

The worker is told which private port to use through an environment
variable (see SupervisorServer.worker_env).

Created on 2026-11-26

@author: cook
"""
import html
import http.client
import json
import os
import socket
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, List, Tuple
from urllib.parse import urlparse

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'aperocore.gui.server.py'
# default environment variable holding the private worker port
WORKER_PORT_ENV = 'APEROCORE_GUI_WORKER_PORT'
# seconds to wait for a proxied worker response
REQUEST_TIMEOUT = 30
# seconds to wait for a worker to stop before killing it
WORKER_STOP_TIMEOUT = 5
# default recovery page texts (applications should pass their own)
DEFAULT_TITLE = 'GUI'
DEFAULT_DOWN_MESSAGE = ('The gui worker is not responding. Restart it to '
                        'continue (running jobs are not stopped).')
DEFAULT_RESTART_LABEL = 'Restart server'
DEFAULT_RESTART_PROMPT = ('Restart the gui worker? Running jobs are not '
                          'stopped.')


# =============================================================================
# Define classes
# =============================================================================
class SupervisorServer(ThreadingHTTPServer):
    """Supervise a disposable gui worker behind a stable public HTTP port."""

    def __init__(self, address: Tuple[str, int], command: List[str],
                 worker_env: str = WORKER_PORT_ENV,
                 title: str = DEFAULT_TITLE,
                 down_message: str = DEFAULT_DOWN_MESSAGE,
                 restart_label: str = DEFAULT_RESTART_LABEL,
                 restart_prompt: str = DEFAULT_RESTART_PROMPT) -> None:
        """Bind the public listener without starting the worker.

        :param address: Public bind host and port.
        :param command: Original gui command, including its interpreter
                        (re-run as the worker).
        :param worker_env: Environment variable that tells the worker which
                           private loopback port to listen on.
        :param title: Recovery page title (the application name).
        :param down_message: Recovery page text when the worker is down.
        :param restart_label: Recovery page restart button label.
        :param restart_prompt: Recovery page restart confirmation text.
        :return: None.
        """
        super().__init__(address, RecoveryHandler)
        self.command = command
        self.worker_env = worker_env
        self.title = title
        self.down_message = down_message
        self.restart_label = restart_label
        self.restart_prompt = restart_prompt
        self.worker: Any = None
        self.backend_port = 0
        self.worker_lock = threading.Lock()
        self.restarting = False
        self.closing = threading.Event()

    def start_worker(self) -> None:
        """Start a fresh dashboard on a private loopback port.

        :return: None.
        """
        if self.closing.is_set():
            return
        with socket.socket() as probe:
            probe.bind(('127.0.0.1', 0))
            self.backend_port = probe.getsockname()[1]
        environment = os.environ.copy()
        environment[self.worker_env] = str(self.backend_port)
        worker_kwargs = dict(env=environment, start_new_session=True)
        self.worker = subprocess.Popen(self.command, **worker_kwargs)
        if self.closing.is_set():
            self.stop_worker()

    def restart_worker(self) -> None:
        """Replace only the dashboard process, not its task process group.

        :return: None.
        """
        try:
            with self.worker_lock:
                if self.closing.is_set():
                    return
                self.stop_worker()
                if self.worker is None or self.worker.poll() is not None:
                    self.start_worker()
        finally:
            self.restarting = False

    def stop_worker(self) -> None:
        """Bound the time spent stopping an unresponsive worker.

        :return: None.
        """
        worker = self.worker
        if worker is None:
            return
        if worker.poll() is None:
            try:
                worker.terminate()
                worker.wait(timeout=WORKER_STOP_TIMEOUT)
                return
            except ProcessLookupError:
                return
            except (subprocess.TimeoutExpired, KeyboardInterrupt):
                pass
            try:
                worker.kill()
                worker.wait(timeout=WORKER_STOP_TIMEOUT)
            except (ProcessLookupError, subprocess.TimeoutExpired,
                    KeyboardInterrupt):
                pass

    def worker_request(self, path: str, body: Any = None) -> dict:
        """Send one short lifecycle request to the private worker.

        :param path: Worker API path.
        :param body: JSON POST data, or None for GET.
        :return: Decoded worker response.
        """
        connection = http.client.HTTPConnection(
            '127.0.0.1', self.backend_port, timeout=2)
        try:
            method = 'GET' if body is None else 'POST'
            data = None if body is None else json.dumps(body)
            connection.request(method, path, data)
            response = connection.getresponse()
            return json.loads(response.read())
        finally:
            connection.close()

    def finish_worker(self) -> None:
        """Shut down the worker with bounded waits and no further restarts.

        :return: None.
        """
        self.closing.set()
        acquired = False
        try:
            acquired = self.worker_lock.acquire(timeout=WORKER_STOP_TIMEOUT)
            if not acquired:
                self.stop_worker()
                return
            try:
                self.worker_request('/api/shutdown', dict())
            except (OSError, ValueError, http.client.HTTPException):
                self.stop_worker()
            else:
                if self.worker is not None:
                    try:
                        self.worker.wait(timeout=WORKER_STOP_TIMEOUT)
                    except subprocess.TimeoutExpired:
                        self.stop_worker()
        except KeyboardInterrupt:
            self.stop_worker()
        finally:
            if acquired:
                self.worker_lock.release()


class RecoveryHandler(BaseHTTPRequestHandler):
    """Proxy normal requests and handle recovery outside the dashboard."""

    def log_message(self, fmt: str, *args: Any) -> None:
        """Suppress HTTP access logs.

        :param fmt: HTTP log format.
        :param args: Log values.
        :return: None.
        """
        _ = fmt, args

    def _send(self, code: int, body: bytes, ctype: str) -> None:
        """Send uncached content, tolerating an abandoned browser request.

        :param code: HTTP response status.
        :param body: Encoded response body.
        :param ctype: Response content type.
        :return: None.
        """
        try:
            self.send_response(code)
            self.send_header('Content-Type', ctype)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def do_GET(self) -> None:
        """Forward reads or return a recovery page if the worker is down.

        :return: None.
        """
        self._proxy()

    def do_POST(self) -> None:
        """Handle restart through the existing permission-gated shutdown API.

        :return: None.
        """
        self.connection.settimeout(REQUEST_TIMEOUT)
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            form = json.loads(body or b'{}')
        except (ValueError, OSError):
            self._send(400, b'{}', 'application/json')
            return
        if urlparse(self.path).path == '/api/shutdown':
            if isinstance(form, dict) and form.get('restart') is True:
                with self.server.worker_lock:
                    if not self.server.restarting:
                        self.server.restarting = True
                        worker = self.server.restart_worker
                        threading.Thread(target=worker, daemon=True).start()
                self._send(202, b'{"restarting":true}', 'application/json')
                return
            self._send(202, b'{}', 'application/json')
            threading.Thread(target=self.server.shutdown,
                             daemon=True).start()
            return
        self._proxy(body)

    def _proxy(self, body: bytes = b'') -> None:
        """Forward one request with a bounded backend timeout.

        :param body: Encoded POST body, empty for GET.
        :return: None.
        """
        connection = http.client.HTTPConnection(
            '127.0.0.1', self.server.backend_port, timeout=REQUEST_TIMEOUT)
        try:
            if self.server.restarting:
                raise ConnectionError()
            headers = dict()
            headers['Content-Type'] = 'application/json'
            connection.request(self.command, self.path, body, headers)
            response = connection.getresponse()
            content = response.read()
            ctype = response.getheader('Content-Type', 'application/json')
            self._send(response.status, content, ctype)
        except (OSError, http.client.HTTPException):
            message = self.server.down_message
            if urlparse(self.path).path in ('/', '/index.html'):
                label = html.escape(self.server.restart_label)
                prompt = json.dumps(self.server.restart_prompt)
                title = html.escape(self.server.title)
                page = '<!doctype html><meta name="viewport" '
                page += 'content="width=device-width,initial-scale=1">'
                page += '<title>' + title + '</title>'
                page += '<h1>' + title + '</h1>'
                page += '<p>' + html.escape(message) + '</p>'
                page += '<button id="btn-shutdown" onclick="restart()">'
                page += label + '</button><p id="status"></p><script>'
                page += 'async function restart(){if(!confirm('
                page += prompt
                page += '))return;try{const r=await fetch("api/shutdown",'
                page += '{method:"POST",headers:{"Content-Type":'
                page += '"application/json"},body:JSON.stringify('
                page += '{restart:true}),signal:AbortSignal.timeout(10000)});'
                page += 'if(!r.ok)throw Error(r.status);'
                page += 'document.getElementById("btn-shutdown")'
                page += '.disabled=true;waitForServer();'
                page += '}catch(e){document.getElementById("status")'
                page += '.textContent=String(e);}}'
                page += 'let attempts=0;async function waitForServer(){'
                page += 'try{const r=await fetch("api/state",{cache:'
                page += '"no-store",signal:AbortSignal.timeout(2000)});'
                page += 'if(!r.ok)throw Error(r.status);'
                page += 'await r.json();location.reload();'
                page += '}catch(e){if(++attempts<60)'
                page += 'setTimeout(waitForServer,1000);else{'
                page += 'document.getElementById("btn-shutdown")'
                page += '.disabled=false;document.getElementById("status")'
                page += '.textContent=String(e);}}}</script>'
                self._send(503, page.encode('utf-8'), 'text/html')
            else:
                content = json.dumps(dict(error=message)).encode('utf-8')
                self._send(503, content, 'application/json')
        finally:
            connection.close()


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('Hello World!')

# =============================================================================
# End of code
# =============================================================================