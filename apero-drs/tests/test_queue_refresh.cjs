const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

const template = fs.readFileSync(path.join(__dirname,
    '../apero/tools/module/processing/gui/queue_template.html'), 'utf8');

function makeContext() {
    const errors = {textContent: ''};
    const timers = new Map();
    let timerId = 0;
    const context = {
        AbortController,
        console: {log() {}},
        document: {getElementById: () => errors},
        apiUrl: url => url,
        setTimeout(callback) { timers.set(++timerId, callback); return timerId; },
        clearTimeout(identifier) { timers.delete(identifier); },
        fetch(url, options) {
            return new Promise((resolve, reject) => {
                options.signal.addEventListener('abort', () => {
                    reject(new Error('request aborted'));
                });
            });
        },
    };
    vm.createContext(context);
    vm.runInContext(template.slice(template.indexOf('function apiFetch('),
        template.indexOf('function escapeHtml(')), context);
    vm.runInContext(template.slice(template.indexOf('var statusLoading ='),
        template.indexOf('function autoRefreshStatus(')), context);
    return {context, errors, timers};
}

const settle = () => new Promise(resolve => setImmediate(resolve));

test('all dashboard scripts parse', () => {
    const scripts = [...template.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)];
    assert.ok(scripts.length);
    for (const script of scripts) { new vm.Script(script[1]); }
});

test('manual refresh replaces a hung request without a stale loading reset',
    async () => {
        const {context, timers} = makeContext();
        context.refreshStatus();
        const previous = context.statusController;
        context.refreshStatus(false, true);
        const current = context.statusController;
        assert.equal(previous.signal.aborted, true);
        await settle();
        assert.equal(context.statusController, current);
        assert.equal(context.statusLoading, true);
        current.abort();
        await settle();
        assert.equal(context.statusLoading, false);
        assert.equal(timers.size, 0);
    });

test('request timeout releases the status loading guard', async () => {
    const {context, errors, timers} = makeContext();
    context.refreshStatus();
    for (const timeout of timers.values()) { timeout(); }
    await settle();
    assert.equal(context.statusLoading, false);
    assert.match(errors.textContent, /request aborted/);
    assert.equal(timers.size, 0);
});

test('polling does not duplicate pending requests and recovers after timeout',
    async () => {
        const {context, timers} = makeContext();
        context.apiGet('/api/state', () => {});
        context.apiGet('/api/state', () => {});
        assert.equal(timers.size, 1);
        for (const timeout of timers.values()) { timeout(); }
        await settle();
        assert.equal(context.pendingGets['/api/state'], undefined);
        context.apiGet('/api/state', () => {});
        assert.equal(timers.size, 1);
        for (const timeout of timers.values()) { timeout(); }
        await settle();
    });

test('manual refresh updates the active Processes and Stats views', () => {
    for (const activeTab of ['tab-processes', 'tab-stats']) {
        const calls = [];
        const context = {
            document: {getElementById: id => ({
                classList: {contains: () => id === activeTab},
            })},
        };
        for (const name of ['refreshStatus', 'refreshState', 'refreshProcesses',
            'refreshStats', 'refreshRunfiles', 'refreshTemplateNames']) {
            context[name] = () => calls.push(name);
        }
        vm.createContext(context);
        const start = template.indexOf('function refreshAll()');
        const end = template.indexOf('\n}', start) + 2;
        vm.runInContext(template.slice(start, end), context);
        context.refreshAll();
        assert.ok(calls.includes(activeTab === 'tab-processes'
            ? 'refreshProcesses' : 'refreshStats'));
    }
});

test('reset disables affected tabs and keeps Processes accessible', () => {
    const ids = ['info', 'generate', 'run', 'actions', 'processes',
        'status', 'stats'];
    const elements = {'reset-block-notice': {hidden: true}};
    for (const id of ids) {
        elements['tab-btn-' + id] = {disabled: false, title: '',
            classList: {toggle() {}}};
        elements['tab-' + id] = {inert: false,
            classList: {toggle() {}}};
    }
    let processRefreshes = 0;
    const context = {
        document: {getElementById: id => elements[id]},
        refreshProcesses: () => { processRefreshes++; },
        refreshStats() {}, render() {},
    };
    vm.createContext(context);
    vm.runInContext(template.slice(template.indexOf('var resetBlocksTabs ='),
        template.indexOf('function setControlTab(')), context);
    context.setResetBlocked(true);
    assert.equal(elements['reset-block-notice'].hidden, false);
    for (const id of ['generate', 'run', 'actions']) {
        assert.equal(elements['tab-btn-' + id].disabled, true);
        assert.equal(elements['tab-' + id].inert, true);
    }
    context.setTab('processes');
    assert.equal(processRefreshes, 1);
    context.setResetBlocked(false);
    assert.equal(elements['reset-block-notice'].hidden, true);
    for (const id of ['generate', 'run', 'actions']) {
        assert.equal(elements['tab-btn-' + id].disabled, false);
        assert.equal(elements['tab-' + id].inert, false);
    }
});