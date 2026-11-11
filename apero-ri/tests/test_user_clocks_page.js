const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

const staticDir = path.join(__dirname, '../apero_ri/static');
const source = fs.readFileSync(
    path.join(staticDir, 'js/user_clocks_page.js'), 'utf8'
);
const table = fs.readFileSync(path.join(staticDir, 'data/zone.tab'), 'utf8');

function page() {
    const pins = {innerHTML: ''};
    const labels = {innerHTML: ''};
    const root = {};
    const elements = {'ari-world-clocks': root, 'ck-labels': labels};
    const document = {
        getElementById: (id) => elements[id] || {},
        createElement: () => ({
            textContent: '',
            get innerHTML() { return this.textContent; }
        })
    };
    const window = {ARI_CLOCK_PAGE: {zoneCoordinatesUrl: '/zone.tab'}};
    const context = {
        document, window, Intl, Date, Promise,
        localStorage: {getItem: () => null},
        fetch: () => Promise.resolve({ok: true, text: () => Promise.resolve(table)})
    };
    const bootstrap = '    paintFormat();\n    bind();\n    initMap();\n'
        + '    loadClocks();\n    loadZoneCoordinates();';
    assert.ok(source.includes(bootstrap));
    const instrumented = source.replace(bootstrap, [
        '    placeLabels = function () {};',
        '    tick = function () {};',
        '    window.clockTest = {state: state, zoneMeta: zoneMeta,',
        '        loadZoneCoordinates: loadZoneCoordinates, buildPins: buildPins};'
    ].join('\n'));
    vm.runInNewContext(instrumented, context);
    const clockTest = window.clockTest;
    clockTest.state.map = {
        projection: (point) => point,
        svg: {querySelector: () => pins}
    };
    return {clockTest, pins, labels};
}

async function loadCoordinates(clockTest) {
    clockTest.loadZoneCoordinates();
    await new Promise((resolve) => setImmediate(resolve));
}

for (const coordinatesFirst of [true, false]) {
    test('new time zones appear on the map, coordinates first: '
        + coordinatesFirst, async () => {
        const {clockTest, pins, labels} = page();
        if (coordinatesFirst) await loadCoordinates(clockTest);
        clockTest.state.clocks = [
            {name: 'Local', timezone: 'LOCAL'},
            {name: 'Amsterdam', timezone: 'Europe/Amsterdam'},
            {name: 'Kathmandu', timezone: 'Asia/Katmandu'},
            {name: 'Eastern', timezone: 'US/Eastern'}
        ];
        clockTest.buildPins();
        if (!coordinatesFirst) {
            assert.doesNotMatch(labels.innerHTML, /Amsterdam/);
            await loadCoordinates(clockTest);
        }
        assert.match(labels.innerHTML, /Amsterdam/);
        assert.match(labels.innerHTML, /Kathmandu/);
        assert.match(labels.innerHTML, /Eastern/);
        assert.match(pins.innerHTML, /translate\(4\.9,52\.4\)/);
        assert.match(pins.innerHTML, /translate\(85\.3,27\.7\)/);
    });
}

test('all browser-selectable time zones have coordinates', async () => {
    const {clockTest} = page();
    await loadCoordinates(clockTest);
    const missing = Intl.supportedValuesOf('timeZone').filter(
        (zone) => !clockTest.zoneMeta[zone]
    );
    assert.deepEqual(missing, []);
    assert.equal(clockTest.zoneMeta['Pacific/Honolulu'].lat, 19.82);
});