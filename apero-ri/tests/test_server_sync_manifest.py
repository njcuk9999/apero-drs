#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Regression coverage for slow peer scans and transport diagnostics."""

import threading

import pytest
import requests

from apero import dev
from apero_ri.ari_api import server_sync
from apero_ri.core.server_sync import crypto
from apero_ri.core.server_sync import engine
from apero_ri.core.server_sync import manifest_jobs
from apero_ri.core.server_sync import store


def test_manifest_returns_while_scan_is_blocked(tmp_path, monkeypatch):
    """HTTP-facing start/status do not wait for a stalled category scan."""
    assert dev is not None
    monkeypatch.setattr(store, 'sync_dir', lambda: tmp_path)
    entered = threading.Event()
    release = threading.Event()
    finished = threading.Event()

    def scan(category):
        entered.set()
        assert release.wait(5)
        return dict(record=dict(h='hash'))

    original_scan = manifest_jobs._scan

    def worker(path, state):
        try:
            original_scan(path, state)
        finally:
            finished.set()

    monkeypatch.setattr(engine, 'scan', scan)
    monkeypatch.setattr(manifest_jobs, '_scan', worker)
    try:
        job = manifest_jobs.start(['users'], 'token-a')
        assert entered.wait(5)
        status = manifest_jobs.read(job['job_id'], 'token-a')
        assert status['status'] == 'running'
        assert status['category'] == 'users'
        assert 'result' not in status
        with pytest.raises(ValueError, match='unknown'):
            manifest_jobs.read(job['job_id'], 'token-b')
    finally:
        release.set()
        assert finished.wait(5)
    status = manifest_jobs.read(job['job_id'], 'token-a')
    assert status['status'] == 'done'
    result = manifest_jobs.read(job['job_id'], 'token-a', 'users')
    assert result == dict(record=dict(h='hash'))


def test_client_polls_and_fetches_categories(monkeypatch):
    """Client waits using short status calls and fetches each category."""
    _, _, token = crypto.new_token()
    client = server_sync.PeerClient('http://example.test', token, 'local')
    calls = []

    def call(action, payload):
        calls.append((action, payload))
        if payload.get('category'):
            return dict(record=dict(h='hash'))
        status = 'running' if action == 'manifest_start' else 'done'
        return dict(job_id='id', status=status)

    monkeypatch.setattr(client, 'call', call)
    monkeypatch.setattr(server_sync, 'POLL_INTERVAL', 0)
    result = client.manifest(['users'])
    assert result == dict(users=dict(record=dict(h='hash')))
    assert [entry[0] for entry in calls] == [
        'manifest_start', 'manifest_status', 'manifest_status']


def test_read_timeout_names_action_and_category(monkeypatch):
    """Read timeouts distinguish slow responses from connection failures."""
    _, _, token = crypto.new_token()
    client = server_sync.PeerClient('http://example.test', token, 'local')

    def post(*args, **kwargs):
        raise requests.ReadTimeout('slow')

    monkeypatch.setattr(requests, 'post', post)
    with pytest.raises(server_sync.PeerError, match=r'fetch \(users\)'):
        client.fetch('users', ['record'])


def test_signed_manifest_routes(tmp_path, monkeypatch):
    """The real peer client can poll authenticated read-only scan routes."""
    from flask import Flask
    from apero_ri.application import server_sync_api_helpers

    monkeypatch.setattr(store, 'sync_dir', lambda: tmp_path)
    monkeypatch.setattr(store, 'secret_dir', lambda: tmp_path)
    monkeypatch.setattr(engine, 'scan', lambda category: dict(item='version'))
    monkeypatch.setattr(server_sync, 'POLL_INTERVAL', 0.01)
    token = store.issue_token('test', 'read', 'tester')
    app = Flask(__name__)

    @app.post('/api/server-sync/peer/<action>')
    def route(action):
        return server_sync_api_helpers.peer_api_view(None, action)

    http = app.test_client()

    def post(url, data, headers, **kwargs):
        path = url.removeprefix('http://example.test')
        response = http.post(path, data=data, headers=headers)
        result = requests.Response()
        result.status_code = response.status_code
        result._content = response.data
        return result

    monkeypatch.setattr(requests, 'post', post)
    client = server_sync.PeerClient('http://example.test', token, 'local')
    assert client.manifest(['users']) == dict(users=dict(item='version'))