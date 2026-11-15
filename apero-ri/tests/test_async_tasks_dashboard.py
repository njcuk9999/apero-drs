#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Regression coverage for async task scopes and named queues."""

import shutil
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest
from flask import Flask

from apero import dev
from apero_ri.application import async_tasks_api_helpers as api
from apero_ri.application import async_task_helpers
from apero_ri.core import auth
from apero_ri.core import task_runner


@pytest.fixture(scope='module', autouse=True)
def profile_free_params() -> None:
    """Use APERO's profile-free test setup for this task test module."""
    dev.get_base_params('SPIROU')


def test_catalog_creates_independent_profile_tasks(tmp_path,
                                                  monkeypatch) -> None:
    """Each enabled profile gets its own schedule and stable task identity."""
    from apero_ri import tasks

    profiles = dict(SPIROU=dict(first=dict(), second=dict()))
    monkeypatch.setattr(auth, 'ASYNC_TASKS_FILE', tmp_path / 'tasks.yaml')
    monkeypatch.setattr(auth, 'load_apero_profiles', lambda **kw: profiles)
    monkeypatch.setattr(tasks, 'TASK_LIST', dict(PROFILE_TASK=object))
    monkeypatch.setattr(tasks, 'TYPE', dict(PROFILE_TASK='PROFILE'))
    saved = dict()
    rows, changed = async_task_helpers.merge_async_task_catalog('SPIROU', saved)
    assert changed
    assert [row['apero_profile'] for row in rows] == ['first', 'second']
    assert len({row['id'] for row in rows}) == 2
    rows[0]['active'] = True
    rows[1]['active'] = False
    merge_args = ['SPIROU', saved]
    again, changed = async_task_helpers.merge_async_task_catalog(*merge_args)
    assert not changed
    assert [row['active'] for row in again] == [True, False]
    assert [row['id'] for row in again] == [row['id'] for row in rows]


def test_parallel_defaults_preserve_task_overrides(tmp_path,
                                                  monkeypatch) -> None:
    """Defaults track future changes without replacing task overrides."""
    from apero_ri import tasks

    monkeypatch.setattr(auth, 'ASYNC_TASKS_FILE', tmp_path / 'tasks.yaml')
    monkeypatch.setattr(auth, 'load_apero_profiles', lambda **kw: dict())
    monkeypatch.setattr(tasks, 'TASK_LIST', dict(PARALLEL_TASK=object))
    monkeypatch.setattr(tasks, 'TYPE', dict(PARALLEL_TASK='INSTRUMENT'))
    monkeypatch.setattr(tasks, 'MULTI_PROCESS', dict(PARALLEL_TASK=True))
    defaults = dict(ncores=3, mp_backend='processes', mp_start_method='spawn')
    async_task_helpers.save_parallel_defaults(defaults)
    saved = dict()
    rows, _ = async_task_helpers.merge_async_task_catalog('SPIROU', saved)
    assert rows[0]['ncores'] == 3
    defaults['ncores'] = 5
    async_task_helpers.save_parallel_defaults(defaults)
    rows, _ = async_task_helpers.merge_async_task_catalog('SPIROU', saved)
    assert rows[0]['ncores'] == 5
    rows[0].update(parallel_override=True, ncores=2)
    rows, _ = async_task_helpers.merge_async_task_catalog('SPIROU', saved)
    assert rows[0]['ncores'] == 2


def test_profile_runtime_only_receives_assigned_profile() -> None:
    """A profile task cannot accidentally execute another profile."""
    profiles = dict(SPIROU=dict(first=dict(), second=dict()))
    params = task_runner.build_run_params(
        'SPIROU', '/tmp/ari-test', profiles, dict(apero_profile='second'))
    assert params['APERO_PROFILE_NAMES'] == ['second']
    assert list(params['APERO_PROFILES']) == ['second']


def test_precomputed_fallback_publishes_and_restores(tmp_path) -> None:
    """Server fallback and CLI publication share the standard output tree."""
    from apero_ri.tasks import apero_sync

    local = tmp_path / 'local'
    other = tmp_path / 'other'
    profile = dict(paths=dict(PATH_OTHER=str(other)))
    params = dict(LOCAL_DATA_DIR=str(local), INSTRUMENT='SPIROU',
                  APERO_PROFILES=dict(first=profile))
    output = local / 'tasks' / 'SPIROU' / 'first' / 'objects' / 'result.json'
    calls = []

    def compute(run_params: dict) -> None:
        """Write a small deterministic task result."""
        calls.append(run_params)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text('computed', encoding='utf-8')
        instance.output_files = [str(output)]

    instance = SimpleNamespace(run_job=compute, output_files=[], info='')
    apero_sync.run_with_precomputed(instance, 'TEST_TASK', params)
    assert len(calls) == 1
    shared = other / 'apero-ri' / 'tasks' / 'SPIROU' / 'first'
    assert (shared / '.TEST_TASK.json').is_file()
    output.unlink()
    apero_sync.run_with_precomputed(instance, 'TEST_TASK', params)
    assert len(calls) == 1
    assert output.read_text(encoding='utf-8') == 'computed'
    (shared / 'objects' / 'result.json').unlink()
    apero_sync.run_with_precomputed(instance, 'TEST_TASK', params)
    assert len(calls) == 2
    (shared / 'objects' / 'result.json').write_text('partial', encoding='utf-8')
    apero_sync.run_with_precomputed(instance, 'TEST_TASK', params)
    assert len(calls) == 3


def test_parallel_management_updates_all_and_checks_permissions(
    tmp_path, monkeypatch,
) -> None:
    """Management defaults preserve overrides until explicitly bulk-reset."""
    from apero_ri import tasks

    monkeypatch.setattr(auth, 'ASYNC_TASKS_FILE', tmp_path / 'tasks.yaml')
    monkeypatch.setattr(auth, 'load_apero_profiles', lambda **kw: dict())
    monkeypatch.setattr(api, 'load_apero_profiles', lambda **kw: dict())
    monkeypatch.setattr(tasks, 'TASK_LIST', dict(PARALLEL_TASK=object))
    monkeypatch.setattr(tasks, 'TYPE', dict(PARALLEL_TASK='INSTRUMENT'))
    monkeypatch.setattr(tasks, 'MULTI_PROCESS', dict(PARALLEL_TASK=True))
    saved = dict(SPIROU=[dict(task_key='PARALLEL_TASK', ncores=2,
                             parallel_override=True)])
    monkeypatch.setattr(api, 'load_async_tasks', lambda: saved)
    monkeypatch.setattr(api, 'save_async_tasks', lambda data: None)
    app = SimpleNamespace(
        _require_async_tasks_perm=lambda: (dict(username='test'), set()),
        _merge_async_task_catalog=async_task_helpers.merge_async_task_catalog,
        _refresh_admin_health_after_change=lambda *args: None,
    )
    payload = dict(action='set_defaults', ncores=4, mp_backend='processes',
                   mp_start_method='spawn')
    flask_app = Flask(__name__)
    with flask_app.test_request_context('/', json=payload):
        assert api.api_async_tasks_save(app).get_json()['success']
    assert saved['SPIROU'][0]['ncores'] == 2
    payload['action'] = 'update_all'
    with flask_app.test_request_context('/', json=payload):
        assert api.api_async_tasks_save(app).get_json()['success']
    assert saved['SPIROU'][0]['ncores'] == 4
    assert not saved['SPIROU'][0]['parallel_override']
    individual = dict(instrument='SPIROU', id=saved['SPIROU'][0]['id'],
                      frequency=6, active=True, ncores=2,
                      mp_backend='threads', mp_start_method='default',
                      parallel_override=True)
    with flask_app.test_request_context('/', json=individual):
        assert api.api_async_tasks_save(app).get_json()['success']
    assert saved['SPIROU'][0]['ncores'] == 2
    assert saved['SPIROU'][0]['parallel_override']
    app._require_async_tasks_perm = lambda: (None, set())
    with flask_app.test_request_context('/', json=payload):
        response, status = api.api_async_tasks_save(app)
    assert status == 401
    assert not response.get_json()['success']


def test_precomputed_checks_restore_to_configured_root(tmp_path,
                                                       monkeypatch) -> None:
    """Check manifests restore into the receiving profile's checks root."""
    from apero_ri.apero_monitoring import core as checks_core
    from apero_ri.tasks import apero_sync

    local = tmp_path / 'local'
    original = tmp_path / 'source_checks'
    receiving = tmp_path / 'server_checks'
    profile = dict(paths=dict(PATH_OTHER=str(tmp_path / 'other')))
    params = dict(LOCAL_DATA_DIR=str(local), INSTRUMENT='SPIROU',
                  APERO_PROFILES=dict(first=profile))
    original.mkdir()
    output = original / '2026-11-15.yaml'
    output.write_text('checks: success', encoding='utf-8')
    monkeypatch.setattr(checks_core, 'resolve_output_root',
                        lambda *args: original)
    apero_sync.publish_precomputed('APERO_CHECK_TASK', params, [str(output)])
    monkeypatch.setattr(checks_core, 'resolve_output_root',
                        lambda *args: receiving)
    files = apero_sync.restore_precomputed('APERO_CHECK_TASK', params)
    assert files == [str(receiving / output.name)]
    assert Path(files[0]).read_text(encoding='utf-8') == 'checks: success'


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
