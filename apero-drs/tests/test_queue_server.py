#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Exercise queue recovery against real crashed and blocked workers."""
import http.client
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Iterator

import pytest

from apero import dev
from apero.tools.module.processing import drs_queue_server as queue_server


WORKER_CODE = '''
import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.path == '/hang':
            threading.Event().wait()
        body = json.dumps(dict(pid=os.getpid(), busy=False)).encode()
        self.send_response(200)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        self.do_GET()
        threading.Thread(target=self.server.shutdown, daemon=True).start()

port = int(os.environ['APERO_QUEUE_GUI_WORKER_PORT'])
server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
server.serve_forever()
server.server_close()
'''


def _request(server: queue_server.QueueServer, path: str,
             body: dict | None = None) -> tuple:
    """Request a public supervisor endpoint.

    :param server: Running queue supervisor.
    :param path: Public request path.
    :param body: POST payload or None for GET.
    :return: HTTP status, content type, cache policy and body.
    """
    connection = http.client.HTTPConnection(*server.server_address, timeout=2)
    try:
        method = 'GET' if body is None else 'POST'
        data = None if body is None else json.dumps(body)
        connection.request(method, path, data)
        response = connection.getresponse()
        return (response.status, response.getheader('Content-Type'),
                response.getheader('Cache-Control'), response.read())
    finally:
        connection.close()


def _wait_worker(server: queue_server.QueueServer, old_pid: int = 0) -> int:
    """Wait briefly for a fresh backend without fixed startup sleeps.

    :param server: Running supervisor.
    :param old_pid: Process ID which must have been replaced.
    :return: New responsive worker PID.
    """
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        status, _, _, body = _request(server, '/api/state')
        if status == 200 and json.loads(body)['pid'] != old_pid:
            return json.loads(body)['pid']
        threading.Event().wait(0.02)
    pytest.fail('Queue worker did not become ready')


@pytest.fixture
def server() -> Iterator[queue_server.QueueServer]:
    """Run an isolated supervisor with a small synthetic queue worker.

    :return: Supervisor with a disposable child process.
    """
    dev.get_base_params('SPIROU')
    command = [sys.executable, '-u', '-c', WORKER_CODE]
    instance = queue_server.QueueServer(('127.0.0.1', 0), command)
    instance.start_worker()
    thread = threading.Thread(target=instance.serve_forever, daemon=True)
    thread.start()
    try:
        _wait_worker(instance)
        yield instance
    finally:
        instance.shutdown()
        instance.server_close()
        with instance.worker_lock:
            instance.stop_worker()
        thread.join(timeout=2)


def test_restart_after_crash(server: queue_server.QueueServer,
                             tmp_path: Path) -> None:
    """Recovery survives a crashed worker and preserves queue files.

    :param server: Isolated running supervisor.
    :param tmp_path: Temporary queue data directory.
    :return: None.
    """
    marker = tmp_path / 'task.yaml'
    marker.write_text('state: pending\n')
    port = server.server_address[1]
    old_pid = server.worker.pid
    server.worker.kill()
    server.worker.wait(timeout=2)
    status, ctype, cache, body = _request(server, '/')
    assert status == 503
    assert ctype == 'text/html'
    assert cache == 'no-store'
    assert b'Restart server' in body
    assert b'api/shutdown' in body
    status, _, _, body = _request(server, '/api/shutdown', dict(restart=True))
    assert status == 202
    assert json.loads(body)['restarting']
    assert _wait_worker(server, old_pid) != old_pid
    assert server.server_address[1] == port
    assert marker.read_text() == 'state: pending\n'
    assert os.getsid(server.worker.pid) == server.worker.pid


def test_restart_with_blocked_request(server: queue_server.QueueServer) -> None:
    """A blocked data request cannot block the independent restart route.

    :param server: Isolated running supervisor.
    :return: None.
    """
    connection = http.client.HTTPConnection(*server.server_address, timeout=2)
    connection.request('GET', '/hang')
    old_pid = server.worker.pid
    try:
        status, _, _, _ = _request(server, '/api/shutdown', dict(restart=True))
        assert status == 202
        assert _wait_worker(server, old_pid) != old_pid
    finally:
        connection.close()


def test_restart_does_not_stop_independent_task(
    server: queue_server.QueueServer,
) -> None:
    """Worker replacement does not signal separately running tasks.

    :param server: Isolated running supervisor.
    :return: None.
    """
    task_code = 'import threading; threading.Event().wait()'
    task = subprocess.Popen([sys.executable, '-c', task_code])
    try:
        old_pid = server.worker.pid
        _request(server, '/api/shutdown', dict(restart=True))
        _wait_worker(server, old_pid)
        assert task.poll() is None
    finally:
        task.terminate()
        task.wait(timeout=2)