const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const {test} = require('node:test');

const source = fs.readFileSync(path.join(__dirname,
    '../apero_ri/static/js/admin_apero_profiles.js'), 'utf8');

function setup() {
    const elements = new Map();
    function element(id = '') {
        let value = '';
        return {
            id, style: {}, disabled: false, checked: false, options: [],
            classList: {contains: () => false, toggle() {}},
            get value() { return value; },
            set value(next) { value = next; },
            set innerHTML(html) { this.options = []; this.html = html; },
            get innerHTML() { return this.html || ''; },
            appendChild(child) { this.options.push(child); },
            addEventListener() {},
            dispatchEvent(event) { this.lastEvent = event.type; },
            setAttribute(name, next) { this[name] = next; },
            focus() { document.activeElement = this; },
        };
    }
    const document = {
        getElementById(id) {
            if (!elements.has(id)) elements.set(id, element(id));
            return elements.get(id);
        },
        querySelector: () => null,
        createElement: () => element(),
        createTextNode: text => ({textContent: text}),
        body: {style: {overflow: 'auto'}},
    };
    const window = {ARI_APERO_PROFILES: {
        labels: {
            FIND_REQUIRED: 'Enter search text', BEFORE: 'Before', AFTER: 'After',
            NO_CHANGES: 'No matching paths', PREVIEW_STALE: 'Preview again',
        }, validateUrl: '/validate',
        listTablesUrl: '/tables',
    }};
    const requests = [];
    // Keep the real editor logic, isolating workflow rendering and bootstrap.
    const marker = '    /* -- Event listeners';
    const end = source.indexOf(marker);
    assert.ok(end > 0);
    const instrumented = source.slice(0, end) + `
        updateWorkflowState = function () {};
        showFieldValidation = function (el, valid, message) {
            el.result = {valid: valid, message: message};
        };
        window.editor = {
            updateDefaultTableSuffixes, refreshTablesFromProfileName,
            setDefaultTableFilters, setTableOptions, replaceDataPaths,
            previewDataPaths, invalidatePathReplacementPreview,
            openPathReplacement, closePathReplacement,
            validatePathNow, testPaths, resetPathTools, PATH_FIELDS,
            tableFilterEdited,
            setPassed() { tablesTestPassed = true; },
            passed() { return tablesTestPassed; },
        };
    })();`;
    vm.runInNewContext(instrumented, {
        window, document, Event, setTimeout, clearTimeout,
        fetch(url, options) {
            requests.push({url, options});
            return Promise.resolve({json: () => Promise.resolve({
                success: true, valid: true,
                tables: ['calib_new', 'calib_old'],
            })});
        },
    });
    return {editor: window.editor, elements, requests,
        get: document.getElementById};
}

test('name changes clear stale selections but preserve custom filters', () => {
    const {editor, get} = setup();
    editor.setDefaultTableFilters('old');
    editor.setTableOptions(['calib_old', 'calib_new'], true);
    get('profile-tbl-calib').value = 'calib_old';
    get('profile-tbl-log').value = 'manual_log';
    get('profile-tbl-suffix-log').value = 'manual_log';
    editor.tableFilterEdited.LOG_TABLENAME = true;
    editor.setPassed();
    get('profile-name').value = 'new';
    editor.updateDefaultTableSuffixes();
    assert.equal(get('profile-tbl-calib').value, 'calib_new');
    assert.equal(get('profile-tbl-log').value, 'manual_log');
    assert.equal(get('profile-tbl-suffix-log').value, 'manual_log');
    assert.equal(editor.passed(), false);
    // A sole table with the wrong suffix must not be reselected.
    editor.setTableOptions(['calib_old'], true);
    get('profile-tbl-calib').value = '';
    editor.updateDefaultTableSuffixes();
    assert.equal(get('profile-tbl-calib').value, '');
});

test('explicit refresh reloads tables and resets custom filters', async () => {
    const {editor, get, requests} = setup();
    get('profile-name').value = 'new';
    get('profile-tbl-calib').value = 'calib_old';
    get('profile-tbl-prefix-calib').value = 'custom_';
    editor.tableFilterEdited.CALIB_TABLENAME = true;
    await editor.refreshTablesFromProfileName();
    assert.equal(requests[0].url, '/tables');
    assert.equal(get('profile-tbl-calib').value, 'calib_new');
    assert.equal(get('profile-tbl-prefix-calib').value, 'calib_');
    assert.equal(editor.tableFilterEdited.CALIB_TABLENAME, false);
});

test('replacement is literal, replaces all occurrences, and only edits paths', () => {
    const {editor, get} = setup();
    get('paths-replace-from').value = 'a.*';
    get('paths-replace-to').value = '$&';
    get('profile-path-raw').value = '/a.*/a.*/raw';
    get('profile-path-red').value = '/unchanged/red';
    get('profile-path-critical-check').value = '/a.*/disabled';
    get('profile-path-critical-check').disabled = true;
    get('profile-name').value = 'a.*';
    get('profile-db-name').value = 'a.*';
    editor.previewDataPaths();
    assert.equal(get('profile-path-raw').value, '/a.*/a.*/raw');
    assert.equal(get('paths-replace-count').textContent, '1');
    assert.equal(get('btn-paths-replace').disabled, false);
    editor.replaceDataPaths();
    assert.equal(get('profile-path-raw').value, '/$&/$&/raw');
    assert.equal(get('profile-path-raw').lastEvent, 'input');
    assert.equal(get('profile-path-red').lastEvent, undefined);
    assert.equal(get('profile-path-critical-check').value, '/a.*/disabled');
    assert.equal(get('profile-name').value, 'a.*');
    assert.equal(get('profile-db-name').value, 'a.*');
    get('paths-replace-to').value = '';
    get('paths-replace-from').value = '$&';
    editor.previewDataPaths();
    editor.replaceDataPaths();
    assert.equal(get('profile-path-raw').value, '///raw');
});

test('opening, previewing, and canceling never mutate form paths', () => {
    const {editor, get} = setup();
    get('profile-path-raw').value = '/old/raw';
    get('paths-replace-from').value = 'old';
    get('paths-replace-to').value = 'new';
    editor.openPathReplacement();
    assert.equal(get('paths-advanced').style.display, 'flex');
    assert.equal(get('btn-paths-replace').disabled, true);
    editor.previewDataPaths();
    editor.closePathReplacement();
    editor.replaceDataPaths();
    assert.equal(get('paths-advanced').style.display, 'none');
    assert.equal(get('profile-path-raw').value, '/old/raw');
    editor.openPathReplacement();
    assert.equal(get('btn-paths-replace').disabled, true);
    assert.equal(get('paths-replace-preview').hidden, true);
});

test('changing replacements or paths prevents applying an outdated preview', () => {
    const {editor, get} = setup();
    get('profile-path-raw').value = '/old/raw';
    get('paths-replace-from').value = 'old';
    get('paths-replace-to').value = 'new';
    editor.previewDataPaths();
    get('paths-replace-to').value = 'different';
    editor.replaceDataPaths();
    assert.equal(get('profile-path-raw').value, '/old/raw');
    assert.equal(get('btn-paths-replace').disabled, true);
    assert.equal(get('paths-replace-status').textContent, 'Preview again');
    editor.previewDataPaths();
    get('profile-path-raw').value = '/old/edited';
    editor.replaceDataPaths();
    assert.equal(get('profile-path-raw').value, '/old/edited');
    assert.equal(get('btn-paths-replace').disabled, true);
});

test('empty searches, unchanged replacements, and no matches cannot apply', () => {
    const {editor, get} = setup();
    get('profile-path-raw').value = '/old/raw';
    editor.previewDataPaths();
    assert.equal(get('paths-replace-status').textContent, 'Enter search text');
    assert.equal(get('btn-paths-replace').disabled, true);
    for (const [from, to] of [['old', 'old'], ['absent', 'new']]) {
        get('paths-replace-from').value = from;
        get('paths-replace-to').value = to;
        editor.previewDataPaths();
        assert.equal(get('paths-replace-status').textContent, 'No matching paths');
        assert.equal(get('btn-paths-replace').disabled, true);
    }
    assert.equal(get('profile-path-raw').value, '/old/raw');
});

test('creation is opt-in and never sent for the optional log file', async () => {
    const {editor, requests} = setup();
    await editor.validatePathNow('profile-path-raw', '/raw', false);
    await editor.validatePathNow('profile-path-red', '/red', true);
    await editor.validatePathNow('profile-path-trigger-log', '/log.txt', true);
    assert.equal(requests[0].url, '/validate?path=%2Fraw');
    assert.equal(requests[0].options, undefined);
    assert.equal(requests[1].options.method, 'POST');
    assert.deepEqual(JSON.parse(requests[1].options.body),
        {path: '/red', create: true});
    assert.equal(requests[2].url, '/validate?path=%2Flog.txt&kind=file');
    assert.equal(requests[2].options, undefined);
});

test('incomplete forms never begin creating directories', () => {
    const {editor, get, requests} = setup();
    get('paths-create-missing').checked = true;
    get('profile-path-raw').value = '/raw';
    editor.testPaths();
    assert.equal(requests.length, 0);
    editor.resetPathTools();
    assert.equal(get('paths-create-missing').checked, false);
    assert.equal(get('paths-advanced').style.display, 'none');
});
