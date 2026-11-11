const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const {test} = require('node:test');

const source = fs.readFileSync(path.join(__dirname,
    '../apero_ri/static/js/download_management_users.js'), 'utf8');

function element(username) {
    const listeners = {};
    const attributes = {};
    return {
        dataset: {dmUser: username}, listeners, attributes,
        id: 'dm-user-info', hidden: true, textContent: '', style: {},
        offsetWidth: 250, offsetHeight: 100, hovered: false,
        addEventListener(type, handler) { listeners[type] = handler; },
        setAttribute(name, value) { attributes[name] = value; },
        removeAttribute(name) { delete attributes[name]; },
        matches() { return this.hovered; },
        contains(target) { return this === target; },
        getBoundingClientRect() { return {left: 300, top: 500, bottom: 520}; }
    };
}

function setup(fetcher) {
    const links = [element('alice'), element('bob'), element('deleted')];
    const card = element();
    const document = element();
    document.activeElement = null;
    document.getElementById = () => card;
    document.querySelectorAll = () => links;
    const window = element();
    window.innerWidth = 360;
    window.innerHeight = 600;
    window.DM_USER_INFO = {
        directoryUrl: '/api/users/directory', loading: 'loading',
        unknown: 'unknown', unavailable: 'unavailable'
    };
    const requests = [];
    let timer;
    vm.runInNewContext(source, {
        window, document, Map,
        fetch(url, options) {
            requests.push({url, options});
            return fetcher();
        },
        clearTimeout() { timer = null; },
        setTimeout(callback) { timer = callback; return 1; }
    });
    return {links, card, document, window, requests,
        leave() { if (timer) timer(); }};
}

const settle = () => new Promise(resolve => setImmediate(resolve));
const response = users => Promise.resolve({
    ok: true, json: () => Promise.resolve({success: true, users})
});

test('focus describes safe text, filters contact, and Escape dismisses', async () => {
    const state = setup(() => response([{
        username: 'alice', full_name: '<img src=x onerror=alert(1)>',
        primary_institution: 'Observatory', groups: ['general'],
        can_view_contact: false, email: 'private@example.test'
    }]));
    const link = state.links[0];
    state.document.activeElement = link;
    link.listeners.focus();
    assert.equal(state.card.textContent, 'loading');
    assert.equal(link.attributes['aria-describedby'], state.card.id);
    await settle();
    assert.equal(state.card.textContent,
        '<img src=x onerror=alert(1)>\nObservatory\ngeneral');
    assert.equal(state.card.hidden, false);
    assert.equal(state.card.style.left, '98px');
    assert.equal(state.card.style.top, '394px');
    assert.equal(state.requests[0].url, '/api/users/directory');
    assert.equal(state.requests[0].options.cache, 'no-store');
    state.document.listeners.keydown({key: 'Escape'});
    assert.equal(state.card.hidden, true);
    assert.equal(link.attributes['aria-describedby'], undefined);
});

test('authorized contact, unknown users, caching, and hover persistence', async () => {
    const state = setup(() => response([{
        username: 'alice', full_name: 'Alice',
        can_view_contact: true, email: 'allowed@example.test'
    }]));
    state.links[0].listeners.mouseenter();
    await settle();
    assert.match(state.card.textContent, /allowed@example.test/);
    state.links[0].listeners.mouseleave();
    state.card.hovered = true;
    state.leave();
    assert.equal(state.card.hidden, false);
    state.card.hovered = false;
    state.card.listeners.mouseleave();
    state.leave();
    assert.equal(state.card.hidden, true);
    state.links[2].listeners.focus();
    await settle();
    assert.equal(state.card.textContent, 'unknown');
    assert.equal(state.requests.length, 1);
});

test('late responses cannot reopen or replace another user card', async () => {
    let resolveFetch;
    const pending = new Promise(resolve => { resolveFetch = resolve; });
    const state = setup(() => pending);
    state.links[0].listeners.focus();
    state.links[1].listeners.focus();
    resolveFetch(await response([
        {username: 'alice', full_name: 'Alice'},
        {username: 'bob', full_name: 'Bob'}
    ]));
    await settle();
    assert.equal(state.card.textContent, 'Bob');
    assert.equal(state.links[0].attributes['aria-describedby'], undefined);
    state.document.listeners.keydown({key: 'Escape'});
    await settle();
    assert.equal(state.card.hidden, true);
});

test('API failure is safe and the next focus retries', async () => {
    let fail = true;
    const state = setup(() => fail
        ? Promise.resolve({ok: false}) : response([]));
    state.links[0].listeners.focus();
    await settle();
    assert.equal(state.card.textContent, 'unavailable');
    state.document.listeners.keydown({key: 'Escape'});
    fail = false;
    state.links[0].listeners.focus();
    await settle();
    assert.equal(state.card.textContent, 'unknown');
    assert.equal(state.requests.length, 2);
});

test('blur closes, focus persists, and outside click dismisses', async () => {
    const state = setup(() => response([]));
    const link = state.links[0];
    state.document.activeElement = link;
    link.listeners.focus();
    await settle();
    link.listeners.mouseleave();
    state.leave();
    assert.equal(state.card.hidden, false);
    state.document.activeElement = null;
    link.listeners.blur();
    state.leave();
    assert.equal(state.card.hidden, true);
    link.listeners.mouseenter();
    state.document.listeners.click({target: {}});
    assert.equal(state.card.hidden, true);
});

test('resize keeps the card inside the viewport when its link moves offscreen', async () => {
    const state = setup(() => response([]));
    state.links[0].listeners.focus();
    await settle();
    state.window.innerHeight = 200;
    state.window.listeners.resize();
    assert.equal(state.card.style.top, '88px');
});