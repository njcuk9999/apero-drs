const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

function element(tag) {
    return {
        tagName: tag, children: [], dataset: {}, value: '', handlers: {},
        classList: { add() {} },
        set innerHTML(value) { this.children = []; },
        appendChild(child) { this.children.push(child); },
        addEventListener(name, handler) { this.handlers[name] = handler; }
    };
}

const elements = {
    'fb-header-row': element('tr'),
    'fb-filter-row': element('tr')
};
const context = {
    window: {},
    document: {
        addEventListener() {},
        getElementById: id => elements[id] || null,
        createElement: element
    },
    clearTimeout,
    setTimeout
};
let source = fs.readFileSync(path.join(__dirname,
    '../apero_ri/static/js/file_browser.js'), 'utf8');
// Stop before initialization; exercise real filter controls without networking.
source = source.replace('    bindPresets();', `
    window.testBrowser = {
        load: function (rows) {
            fbAllRows = rows;
            fbColFilters = {};
            fbApplyFilterSort();
        },
        rows: function () { return fbFilteredRows; },
        filters: function () { return fbColFilters; }
    };
    return;
    bindPresets();`);
vm.runInNewContext(source, context);

function control(column) {
    return elements['fb-filter-row'].children
        .flatMap(cell => cell.children)
        .find(input => input.dataset.col === column);
}
function enter(column, value) {
    const input = control(column);
    input.value = value;
    input.handlers.keydown({ key: 'Enter', preventDefault() {} });
}
const browser = context.window.testBrowser;
const rows = Array.from({ length: 25 }, (_, index) => ({
    FILENAME: `TargetAbC_${index}s.fits`,
    KW_OUTPUT: index % 2 ? 'DRS_POST_S' : 'drs_post_s',
    KW_PI_NAME: `ObserverAbC_${index}`
}));
browser.load(rows);
enter('FILENAME', 'TARGETABC_1');
assert.equal(browser.rows().length, 11);
assert.equal(control('FILENAME').value, 'TARGETABC_1');
assert.equal(browser.filters().FILENAME, 'TARGETABC_1');
enter('FILENAME', 'targetabc_2');
assert.equal(browser.rows().length, 6);
enter('KW_PI_NAME', 'oBSERVERaBc_24');
assert.equal(browser.rows().length, 1);
assert.equal(browser.rows()[0].FILENAME, rows[24].FILENAME);
enter('FILENAME', 'not-present');
assert.equal(browser.rows().length, 0);

browser.load(rows);
const output = control('KW_OUTPUT');
assert.equal(output.tagName, 'select');
assert.ok(output.children.some(option => option.value === 'DRS_POST_S'));
output.value = 'DRS_POST_S';
output.handlers.change();
assert.equal(browser.rows().length, 25);
assert.ok(control('KW_OUTPUT').children
    .some(option => option.value === 'DRS_POST_S' && option.selected));
