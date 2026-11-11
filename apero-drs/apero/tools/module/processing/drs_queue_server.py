#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Keep queue dashboard recovery independent of its worker process."""
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

from aperocore.base import base
from aperocore import drs_lang

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero.tools.module.processing.drs_queue_server'
__version__ = base.__version__
__date__ = base.__date__
__authors__ = base.__authors__
WORKER_PORT_ENV = 'APERO_QUEUE_GUI_WORKER_PORT'
REQUEST_TIMEOUT = 30
textentry = drs_lang.textentry


# =============================================================================
# Define classes
# =============================================================================
class QueueServer(ThreadingHTTPServer):
    """Supervise a disposable dashboard behind a stable public HTTP port."""

    def __init__(self, address: Tuple[str, int], command: List[str]) -> None:
        """Bind the public listener without starting the worker.

        :param address: Public bind host and port.
        :param command: Original queue command, including its interpreter.
        :return: None.
        """
        super().__init__(address, RecoveryHandler)
        self.command = command
        self.worker: Any = None
        self.backend_port = 0
        self.worker_lock = threading.Lock()
        self.restarting = False

    def start_worker(self) -> None:
        """Start a fresh dashboard on a private loopback port.

        :return: None.
        """
        with socket.socket() as probe:
            probe.bind(('127.0.0.1', 0))
            self.backend_port = probe.getsockname()[1]
        environment = os.environ.copy()
        environment[WORKER_PORT_ENV] = str(self.backend_port)
        self.worker = subprocess.Popen(self.command, env=environment)

    def restart_worker(self) -> None:
        """Replace only the dashboard process, not its task process group.

        :return: None.
        """
        try:
            with self.worker_lock:
                self.stop_worker()
                self.start_worker()
        finally:
            self.restarting = False

    def stop_worker(self) -> None:
        """Bound the time spent stopping an unresponsive worker.

        :return: None.
        """
        if self.worker is None:
            return
        if self.worker.poll() is None:
            self.worker.terminate()
            try:
                self.worker.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.worker.kill()
                self.worker.wait(timeout=5)
        else:
            self.worker.wait()

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
        """Allow a responsive worker to finish its action before exiting.

        :return: None.
        """
        with self.worker_lock:
            try:
                self.worker_request('/api/shutdown', dict())
            except (OSError, ValueError, http.client.HTTPException):
                self.stop_worker()
            else:
                self.worker.wait()


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
            message = textentry('40-513-00044')
            if urlparse(self.path).path in ('/', '/index.html'):
                label = html.escape(textentry('40-513-00045'))
                prompt = json.dumps(textentry('40-513-00046'))
                page = '<!doctype html><meta name="viewport" '
                page += 'content="width=device-width,initial-scale=1">'
                page += '<title>APERO Queue</title><h1>APERO Queue</h1>'
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