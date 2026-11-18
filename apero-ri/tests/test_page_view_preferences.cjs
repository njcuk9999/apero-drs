const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

function node(label) {
    return {
        dataset: {sortLabel: label}, textContent: label,
        children: [], classList: {toggle() {}}
    };
}
const cards = [node('Zulu'), node('alpha'), node('Beta')];
const collection = {
    classList: {toggle(name, enabled) { this[name] = enabled; }},
    children: cards,
    appendChild(item) {
        this.children.splice(this.children.indexOf(item), 1);
        this.children.push(item);
    }
};
const handlers = {};
const buttons = ['cards', 'list'].map(view => ({
    dataset: {ariView: view},
    classList: {toggle() {}},
    setAttribute() {},
    addEventListener(name, callback) { handlers[view + name] = callback; }
}));
const sort = {
    value: 'asc',
    addEventListener(name, callback) { handlers.sort = callback; }
};
const control = {
    dataset: {
        pageId: 'home.data_portal', saveUrl: '/api/user/prefs/save',
        view: 'list', sort: 'asc'
    },
    querySelectorAll() { return buttons; },
    querySelector(selector) {
        if (selector === '[data-ari-sort]') return sort;
        return null;
    },
    closest() { return {
        querySelector() { return collection; }
    }; }
};
const fetches = [];
const context = {
    document: {querySelectorAll() { return [control]; }},
    fetch(url, options) {
        fetches.push(JSON.parse(options.body));
        return Promise.resolve({ok: true});
    },
    Promise,
    Array
};
const source = fs.readFileSync(path.join(__dirname,
    '../apero_ri/static/js/page_view_preferences.js'), 'utf8');
vm.runInNewContext(source, context);

assert.deepEqual(collection.children.map(item => item.textContent),
                 ['alpha', 'Beta', 'Zulu']);
assert.equal(collection.classList['ari-view-collection--list'], true);
handlers.cardsclick();
assert.equal(control.dataset.view, 'cards');
sort.value = 'desc';
handlers.sort();
assert.equal(control.dataset.sort, 'desc');
assert.deepEqual(collection.children.map(item => item.textContent),
                 ['Zulu', 'Beta', 'alpha']);
assert.equal(fetches.at(-1).page_view.view, 'cards');
