#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Regression coverage for async task scopes and named queues."""

import shutil
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest
from flask import Flask

from apero_ri.application import async_tasks_api_helpers as api
from apero_ri.core import task_runner


def test_status_includes_every_named_queue(monkeypatch) -> None:
    """Queue polling returns runtime states for all concurrent workers."""
    queue = dict(named_queues=dict(
        global_queue=dict(current_info=None, queue_info=[]),
        nirps=dict(
            current_info=dict(task_id='nirps-current'),
            queue_info=[dict(task_id='nirps-pending')],
        ),
        spirou=dict(
            current_info=dict(task_id='spirou-current'),
            queue_info=[],
        ),
    ))
    monkeypatch.setattr(task_runner, 'get_status', lambda: queue)
    monkeypatch.setattr(
        task_runner, 'get_task_status',
        lambda tid: dict(found=True, status='in_progress'),
    )
    monkeypatch.setattr(api, 'load_async_tasks', lambda: {})
    app = SimpleNamespace(
        _require_async_tasks_perm=lambda: (dict(username='test'), set())
    )
    with Flask(__name__).test_request_context('/?ids='):
        data = api.api_async_tasks_status(app).get_json()
    assert set(data['statuses']) == {
        'nirps-current', 'nirps-pending', 'spirou-current',
    }


def test_empty_error_file_does_not_scan_directory(tmp_path, monkeypatch):
    """Empty error files are legitimate and need no legacy directory scan."""
    info = tmp_path / 'info.md'
    error = tmp_path / 'error.txt'
    info.write_text('finished', encoding='utf-8')
    error.write_text('', encoding='utf-8')
    monkeypatch.setattr(
        task_runner, '_task_info_file_path', lambda scope, tid: info
    )
    monkeypatch.setattr(
        task_runner, '_task_error_file_path', lambda scope, tid: error
    )

    def unexpected_scan(*args):
        raise AssertionError('Existing files should use direct lookup')

    monkeypatch.setattr(
        task_runner, '_resolve_existing_task_data_file', unexpected_scan
    )
    assert task_runner.get_persisted_task_info_error('id', 'NIRPS') == {
        'info': 'finished', 'error': '',
    }


def test_dashboard_ignores_stale_responses_and_merges_queues() -> None:
    """Exercise the actual JS with delayed fetches across instrument tabs."""
    node = shutil.which('node')
    if node is None:
        pytest.skip('Node.js is required for the dashboard runtime test')
    script_path = (
        Path(__file__).parents[1] / 'apero_ri' / 'static' / 'js'
        / 'admin_async_tasks.js'
    )
    script = r"""
const fs = require('fs');
const vm = require('vm');
const assert = require('assert');
let pending = [];
let scheduled = 0;
const context = {
    window: {ARI_ASYNC_TASKS: {instruments: [], urls: {
        list: '/list', globalList: '/global'
    }}},
    document: {getElementById: () => null,
        readyState: 'loading', addEventListener: () => {}},
    AbortController, console,
    setTimeout: () => {scheduled++; return scheduled;},
    clearTimeout: () => {},
    fetch: () => new Promise(resolve => pending.push(resolve))
};
vm.createContext(context);
let source = fs.readFileSync(process.argv[1], 'utf8');
source = source.replace(/\}\(\)\);\s*$/, `
window.testDashboard = {
    combinedQueue, loadTasks, loadGlobalTasks, pollStatus,
    scope: value => {currentInstrument = value; viewVersion++;},
    tasks: () => allTasks,
    loading: () => taskListLoading,
    stubRender: () => {
        renderTaskLists = () => {};
        updateRunningBadge = () => {};
        showToast = message => {throw new Error(message);};
    }
};
}());`);
vm.runInContext(source, context);
const dashboard = context.window.testDashboard;
dashboard.stubRender();
(async () => {
    dashboard.scope('SPIROU');
    const old = dashboard.loadTasks();
    dashboard.scope('NIRPS');
    const current = dashboard.loadTasks();
    assert.equal(dashboard.loading(), true);
    pending[1]({json: async () => ({
        success: true, tasks: [{id: 'nirps'}]
    })});
    await current;
    pending[0]({json: async () => ({
        success: true, tasks: [{id: 'spirou'}]
    })});
    await old;
    assert.equal(dashboard.loading(), false);
    assert.equal(dashboard.tasks()[0].id, 'nirps');
    dashboard.pollStatus();
    dashboard.scope('__GLOBAL__');
    const global = dashboard.loadGlobalTasks();
    pending[3]({json: async () => ({
        success: true, tasks: [{id: 'global'}]
    })});
    await global;
    pending[2]({json: async () => ({
        success: true, statuses: {global: {status: 'wrong-scope'}}
    })});
    await new Promise(resolve => setImmediate(resolve));
    assert.equal(dashboard.tasks()[0].id, 'global');
    assert.equal(dashboard.tasks()[0].runtime, undefined);
    assert.equal(scheduled, 0);
    const merged = dashboard.combinedQueue({named_queues: {
        global: {current: null, queue: []},
        nirps: {current: ['NIRPS', 'one'],
            current_info: {task_id: 'one'},
            queue: [['NIRPS', 'pending']],
            queue_info: [{task_id: 'pending'}]},
        spirou: {current: ['SPIROU', 'two'],
            current_info: {task_id: 'two'}, queue: []}
    }});
    assert.equal(merged.current[1], 'one');
    assert.equal(merged.additional_currents[0][1], 'two');
    assert.equal(merged.queue[0][1], 'pending');
    assert.equal(merged.queue_length, 1);
})().catch(error => {console.error(error); process.exitCode = 1;});
"""
    subprocess.run(
        [node, '-e', script, str(script_path)],
        check=True,
        capture_output=True,
        text=True,
        timeout=15,
    )
