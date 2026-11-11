'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

const script = fs.readFileSync(path.join(__dirname, '../apero_ri/static/js/awards.js'), 'utf8');
const labels = {
    hours: 'Hours', issues: 'Issues', active_days: 'Active days',
    bytes: 'Bytes', files: 'Files', empty: 'No results',
    gold: 'Gold', silver: 'Silver', bronze: 'Bronze'
};

function render(rows, kind, instrument = 'SPIROU') {
    const list = {innerHTML: ''};
    const board = {
        dataset: {awKind: kind, awInstrument: instrument},
        querySelector: () => list
    };
    const document = {
        getElementById: (id) => ({
            textContent: JSON.stringify(id === 'aw-labels' ? labels : rows)
        }),
        querySelectorAll: () => [board]
    };
    vm.runInNewContext(script, {document});
    return list.innerHTML;
}

function users(selfIndex) {
    return Array.from({length: 15}, (_, index) => ({
        username: 'user' + String(index).padStart(2, '0'),
        who: 'Person ' + index,
        is_self: index === selfIndex,
        active_days: 15 - index,
        total_hours: 15 - index,
        download_bytes: 15 - index,
        download_files: 15 - index,
        instruments: {SPIROU: 15 - index}
    }));
}

for (const kind of ['activity', 'instrument', 'service', 'bytes', 'files']) {
    test(kind + ' shows the top ten and the viewer outside the ranking', () => {
        const html = render(users(13), kind);
        assert.equal((html.match(/class="aw-entry/g) || []).length, 11);
        assert.match(html, /Person 9/);
        assert.doesNotMatch(html, /Person 10/);
        assert.match(html, /aw-entry--self aw-entry--outside/);
        assert.match(html, /<span class="aw-rank">14<\/span>/);
        assert.match(html, /Person 13/);
    });
    test(kind + ' does not duplicate the viewer in the top ten', () => {
        const html = render(users(3), kind);
        assert.equal((html.match(/class="aw-entry/g) || []).length, 10);
        assert.equal((html.match(/aw-entry--self/g) || []).length, 1);
    });
}

test('a viewer without activity appears unranked and content is escaped', () => {
    const html = render([{
        username: '<user>', who: '<script>bad()</script>', is_self: true
    }], 'activity');
    assert.match(html, /aw-entry--self aw-entry--outside/);
    assert.match(html, /<span class="aw-rank">&mdash;<\/span>/);
    assert.match(html, /&lt;script&gt;bad\(\)&lt;\/script&gt;/);
    assert.doesNotMatch(html, /<script>/);
});

test('empty categories without a viewer show the empty state', () => {
    assert.match(render([], 'activity'), /No results/);
});