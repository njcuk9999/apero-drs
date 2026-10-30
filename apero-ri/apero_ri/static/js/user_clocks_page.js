(function () {
    'use strict';

    var config = window.ARI_CLOCK_PAGE || {};
    var apiUrl = String(config.apiUrl || '');
    var root = document.getElementById('ari-world-clocks');
    if (!root) return;

    var get = function (id) { return document.getElementById(id); };
    var grid = get('ck-grid');
    var rows = get('ck-rows');
    var mapState = get('ck-map-state');
    var localZone = Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC';
    var zoneMeta = {
        UTC: {lat: 51.48, lon: 0},
        'America/Toronto': {lat: 45.50, lon: -73.57},
        'America/Montreal': {lat: 45.50, lon: -73.57},
        'America/New_York': {lat: 40.71, lon: -74.01},
        'America/Los_Angeles': {lat: 34.05, lon: -118.24},
        'Europe/London': {lat: 51.51, lon: -0.13},
        'Europe/Paris': {lat: 48.86, lon: 2.35},
        'Pacific/Honolulu': {lat: 19.82, lon: -155.47},
        'Asia/Tokyo': {lat: 35.68, lon: 139.69},
        'Australia/Sydney': {lat: -33.87, lon: 151.21},
        'Asia/Kolkata': {lat: 19.08, lon: 72.88},
        'Asia/Shanghai': {lat: 31.23, lon: 121.47},
        'Asia/Seoul': {lat: 37.57, lon: 126.98},
        'America/Chicago': {lat: 41.88, lon: -87.63},
        'America/Phoenix': {lat: 33.45, lon: -112.07},
        'America/Sao_Paulo': {lat: -23.55, lon: -46.63},
        'Europe/Zurich': {lat: 47.38, lon: 8.54},
        'Europe/Berlin': {lat: 52.52, lon: 13.41},
        'Europe/Madrid': {lat: 40.42, lon: -3.70},
        'Africa/Casablanca': {lat: 33.57, lon: -7.59},
        'Australia/Perth': {lat: -31.95, lon: 115.86},
        'Pacific/Auckland': {lat: -36.85, lon: 174.76}
    };
    var state = {
        offset: 0,
        h12: false,
        clocks: [],
        map: null,
        plannerHour: null,
        lastMapMinute: null,
        plannerDate: dateKey(new Date()),
        baseDate: null,
        baseRealTime: null
    };
    var formatters = {};
    var weekdays = {Sun: 0, Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6};
    var radians = Math.PI / 180;

    try {
        state.h12 = localStorage.getItem('clock-h12') === '1';
    } catch (error) {
        state.h12 = false;
    }

    function dateKey(date) {
        return date.getFullYear() + '-'
            + String(date.getMonth() + 1).padStart(2, '0') + '-'
            + String(date.getDate()).padStart(2, '0');
    }

    function dateStart(key) {
        var date = key.split('-').map(Number);
        return new Date(date[0], date[1] - 1, date[2]);
    }

    function actualZone(zone) {
        return zone === 'LOCAL' ? localZone : zone;
    }

    function now() {
        var current = Date.now();
        var base = state.baseDate === null ? current : state.baseDate;
        var elapsed = state.baseRealTime === null
            ? 0 : current - state.baseRealTime;
        return new Date(base + elapsed + state.offset * 60000);
    }

    function escapeHtml(value) {
        var element = document.createElement('span');
        element.textContent = String(value == null ? '' : value);
        return element.innerHTML;
    }

    function parts(date, zone) {
        var key = actualZone(zone);
        var formatter = formatters[key];
        if (!formatter) {
            formatter = formatters[key] = new Intl.DateTimeFormat('en-US', {
                timeZone: key,
                hourCycle: 'h23',
                weekday: 'short',
                year: 'numeric',
                month: 'numeric',
                day: 'numeric',
                hour: 'numeric',
                minute: 'numeric',
                second: 'numeric'
            });
        }
        var values = {};
        formatter.formatToParts(date).forEach(function (part) {
            values[part.type] = part.value;
        });
        return {
            y: Number(values.year),
            mo: Number(values.month),
            d: Number(values.day),
            h: Number(values.hour) % 24,
            mi: Number(values.minute),
            s: Number(values.second),
            wd: weekdays[values.weekday]
        };
    }

    function offsetOf(date, zone) {
        var value = parts(date, zone);
        var localUtc = Date.UTC(
            value.y, value.mo - 1, value.d,
            value.h, value.mi, value.s
        );
        return Math.round((localUtc - Math.floor(date / 1000) * 1000) / 60000);
    }

    function dayNumber(value) {
        return Date.UTC(value.y, value.mo - 1, value.d) / 86400000;
    }

    function formatTime(date, zone, seconds) {
        var key = actualZone(zone) + ':' + seconds + ':' + state.h12;
        var formatter = formatters[key + ':time'];
        if (!formatter) {
            formatter = formatters[key + ':time'] =
                new Intl.DateTimeFormat(undefined, {
                    timeZone: actualZone(zone),
                    hour: '2-digit',
                    minute: '2-digit',
                    second: seconds ? '2-digit' : undefined,
                    hourCycle: state.h12 ? 'h12' : 'h23'
                });
        }
        return formatter.format(date);
    }

    function formatDate(date, zone, longDate) {
        return new Intl.DateTimeFormat(undefined, {
            timeZone: actualZone(zone),
            weekday: longDate ? 'long' : 'short',
            day: 'numeric',
            month: longDate ? 'long' : 'short'
        }).format(date);
    }

    function formatSpan(minutes) {
        var amount = Math.abs(minutes);
        var hours = Math.floor(amount / 60);
        var remainder = amount % 60;
        return (hours ? hours + ' h' : '')
            + (hours && remainder ? ' ' : '')
            + (remainder ? remainder + ' min' : '') || '0 h';
    }

    function utcLabel(minutes) {
        var amount = Math.abs(minutes);
        var sign = minutes < 0 ? '−' : '+';
        var hours = Math.floor(amount / 60);
        var remainder = amount % 60;
        return 'UTC' + sign + hours
            + (remainder ? ':' + String(remainder).padStart(2, '0') : '');
    }

    function dayStatus(hour, weekday) {
        if (hour < 7 || hour >= 23) return 'asleep';
        if (weekday === 0 || weekday === 6) return 'weekend';
        return hour >= 9 && hour < 17 ? 'work' : 'awake';
    }

    function subsolar(date) {
        var days = (date.getTime() - Date.UTC(2000, 0, 1, 12)) / 86400000;
        var anomaly = (357.529 + 0.98560028 * days) * radians;
        var meanLong = 280.459 + 0.98564736 * days;
        var longitude = (meanLong + 1.915 * Math.sin(anomaly)
            + 0.020 * Math.sin(2 * anomaly)) * radians;
        var obliquity = (23.439 - 0.00000036 * days) * radians;
        var rightAscension = Math.atan2(
            Math.cos(obliquity) * Math.sin(longitude), Math.cos(longitude)
        ) / radians;
        var declination = Math.asin(
            Math.sin(obliquity) * Math.sin(longitude)
        ) / radians;
        var gmst = (280.46061837 + 360.98564736629 * days) % 360;
        var sunLon = ((rightAscension - gmst) % 360 + 540) % 360 - 180;
        return [sunLon, declination];
    }

    function sunAltitude(lon, lat, sun) {
        var cosine = Math.sin(lat * radians) * Math.sin(sun[1] * radians)
            + Math.cos(lat * radians) * Math.cos(sun[1] * radians)
            * Math.cos((lon - sun[0]) * radians);
        return 90 - Math.acos(Math.max(-1, Math.min(1, cosine))) / radians;
    }

    function clockList() {
        var local = state.clocks.filter(function (clock) {
            return actualZone(clock.timezone) === localZone;
        })[0];
        if (local) {
            local.you = true;
            return [local].concat(state.clocks.filter(function (clock) {
                return clock !== local;
            }));
        }
        return [{name: 'Your time', timezone: 'LOCAL', you: true}]
            .concat(state.clocks);
    }

    function clockFace() {
        var ticks = '';
        for (var index = 0; index < 60; index += 1) {
            var major = index % 5 === 0;
            var angle = index * 6 * radians;
            var inner = major ? 36 : 40;
            ticks += '<line class="tick" stroke-width="'
                + (major ? 2.2 : .8) + '" x1="'
                + (inner * Math.sin(angle)).toFixed(2) + '" y1="'
                + (-inner * Math.cos(angle)).toFixed(2) + '" x2="'
                + (44 * Math.sin(angle)).toFixed(2) + '" y2="'
                + (-44 * Math.cos(angle)).toFixed(2) + '"/>';
        }
        return '<svg class="ck-face" viewBox="-50 -50 100 100" '
            + 'aria-hidden="true"><circle class="rim" r="48"/>' + ticks
            + '<line class="hh" stroke-width="4" y1="6" y2="-24"/>'
            + '<line class="mh" stroke-width="2.6" y1="8" y2="-36"/>'
            + '<line class="sh" stroke-width="1.2" y1="12" y2="-40"/>'
            + '<circle class="hub" r="3"/></svg>';
    }

    function setHands(svg, value) {
        var minute = value.mi + value.s / 60;
        var hour = (value.h % 12) + minute / 60;
        svg.querySelector('.hh').setAttribute('transform',
            'rotate(' + hour * 30 + ')');
        svg.querySelector('.mh').setAttribute('transform',
            'rotate(' + minute * 6 + ')');
        svg.querySelector('.sh').setAttribute('transform',
            'rotate(' + value.s * 6 + ')');
    }

    function buildCards() {
        var clocks = clockList();
        if (!clocks.length) {
            grid.innerHTML = '<p class="ck-state">No clocks configured.</p>';
            return;
        }
        grid.innerHTML = clocks.map(function (clock, index) {
            return '<article class="ck-card' + (clock.you ? ' is-you' : '')
                + '" data-i="' + index + '">' + clockFace()
                + '<div class="ck-info"><div class="ck-city"><i '
                + 'aria-hidden="true"></i><span>'
                + escapeHtml(clock.name) + '</span></div>'
                + '<div class="ck-time num"></div><div class="ck-sub"></div>'
                + '<div class="ck-diff"></div>'
                + '<span class="ck-badge"></span></div></article>';
        }).join('');
    }

    function renderCards(date, sun) {
        var local = parts(date, 'LOCAL');
        var localOffset = offsetOf(date, 'LOCAL');
        var clocks = clockList();
        Array.prototype.forEach.call(grid.querySelectorAll('.ck-card'),
            function (card, index) {
                var clock = clocks[index];
                var value = parts(date, clock.timezone);
                var offset = offsetOf(date, clock.timezone);
                var meta = zoneMeta[actualZone(clock.timezone)];
                var isDay = meta
                    ? sunAltitude(meta.lon, meta.lat, sun) > -0.833
                    : value.h >= 7 && value.h < 19;
                setHands(card.querySelector('.ck-face'), value);
                card.classList.toggle('is-day', isDay);
                card.classList.toggle('is-night', !isDay);
                card.querySelector('.ck-city i').className = isDay
                    ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
                card.querySelector('.ck-time').textContent =
                    formatTime(date, clock.timezone, false);
                var delta = dayNumber(value) - dayNumber(local);
                var dayWord = delta === 0 ? 'Today'
                    : delta === 1 ? 'Tomorrow'
                    : delta === -1 ? 'Yesterday' : '';
                card.querySelector('.ck-sub').textContent =
                    (clock.you || !dayWord ? '' : dayWord + ' · ')
                    + formatDate(date, clock.timezone, false)
                    + ' · ' + utcLabel(offset);
                var difference = offset - localOffset;
                var relative = clock.you ? actualZone(clock.timezone)
                    : difference === 0 ? 'Same time'
                    : formatSpan(difference) + (difference > 0
                        ? ' ahead of you' : ' behind you');
                card.querySelector('.ck-diff').textContent = relative;
                var status = dayStatus(value.h, value.wd);
                var badge = card.querySelector('.ck-badge');
                badge.className = 'ck-badge ' + status;
                badge.textContent = status === 'work' ? 'Working hours'
                    : status === 'awake' ? 'Awake'
                    : status === 'weekend' ? 'Weekend' : 'Asleep';
            });
    }

    function loadScript(source) {
        return new Promise(function (resolve, reject) {
            var script = document.createElement('script');
            script.src = source;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    function initMap() {
        var cdn = 'https://cdn.jsdelivr.net/npm/';
        var libraries = [
            'd3-array@3.2.4/dist/d3-array.min.js',
            'd3-geo@3.1.1/dist/d3-geo.min.js',
            'topojson-client@3.1.0/dist/topojson-client.min.js'
        ];
        return libraries.reduce(function (promise, library) {
            return promise.then(function () { return loadScript(cdn + library); });
        }, Promise.resolve()).then(function () {
            return fetch(cdn + 'world-atlas@2.0.2/land-110m.json')
                .then(function (response) {
                    if (!response.ok) throw new Error('Map request failed');
                    return response.json();
                });
        }).then(function (topology) {
            var sphere = {type: 'Sphere'};
            var projection = d3.geoNaturalEarth1().fitWidth(960, sphere);
            var path = d3.geoPath(projection);
            var height = Math.ceil(path.bounds(sphere)[1][1]);
            var svg = get('ck-svg');
            svg.setAttribute('viewBox', '0 0 960 ' + height);
            svg.innerHTML = '<defs><radialGradient id="ck-sunglow">'
                + '<stop offset="0" stop-color="#ffd27a" stop-opacity=".55"/>'
                + '<stop offset="1" stop-color="#ffd27a" stop-opacity="0"/>'
                + '</radialGradient><clipPath id="ck-clip"><path d="'
                + path(sphere) + '"/></clipPath></defs>'
                + '<path class="ck-sphere" d="' + path(sphere) + '"/>'
                + '<path class="ck-grat" d="' + path(d3.geoGraticule10())
                + '"/><path class="ck-land" d="'
                + path(topojson.feature(topology, topology.objects.land))
                + '"/><g class="ck-night" clip-path="url(#ck-clip)"></g>'
                + '<path class="ck-term" clip-path="url(#ck-clip)"/>'
                + '<g class="ck-sun"><circle class="ck-sunglow" r="34"/>'
                + '<circle class="ck-sundot" r="6"/></g>'
                + '<g class="ck-pins"></g>';
            state.map = {projection: projection, path: path, svg: svg};
            mapState.hidden = true;
            buildPins();
            tick();
        }).catch(function () {
            mapState.textContent = 'Map data could not be loaded.';
        });
    }

    function pinClocks() {
        return clockList().filter(function (clock) {
            return !!zoneMeta[actualZone(clock.timezone)];
        });
    }

    function buildPins() {
        if (!state.map) return;
        var clocks = pinClocks();
        state.map.svg.querySelector('.ck-pins').innerHTML = clocks.map(
            function (clock) {
                var meta = zoneMeta[actualZone(clock.timezone)];
                var point = state.map.projection([meta.lon, meta.lat]);
                var index = clockList().indexOf(clock);
                return '<g class="ck-pin' + (clock.you ? ' is-you' : '')
                    + '" data-i="' + index + '" transform="translate('
                    + point[0].toFixed(1) + ',' + point[1].toFixed(1)
                    + ')"><circle class="ring" r="5"/>'
                    + '<circle class="dot" r="5"/></g>';
            }
        ).join('');
        get('ck-labels').innerHTML = clocks.map(function (clock) {
            var index = clockList().indexOf(clock);
            return '<div class="ck-label" data-i="' + index + '"><b>'
                + escapeHtml(clock.name)
                + '</b><span class="num"></span></div>';
        }).join('');
        placeLabels();
    }

    function placeLabels() {
        if (!state.map) return;
        var mapBox = get('ck-map').getBoundingClientRect();
        var svgBox = state.map.svg.getBoundingClientRect();
        var scale = svgBox.width / 960;
        var svgTop = svgBox.top - mapBox.top;
        var svgBottom = svgBox.bottom - mapBox.top;
        var bandHeight = svgTop;
        var clocks = pinClocks();
        var labels = Array.prototype.slice.call(get('ck-labels').children);
        var items = labels.map(function (label, index) {
            var meta = zoneMeta[actualZone(clocks[index].timezone)];
            var point = state.map.projection([meta.lon, meta.lat]);
            return {
                label: label,
                index: Number(label.getAttribute('data-i')),
                x: point[0] * scale,
                y: svgTop + point[1] * scale,
                width: label.offsetWidth,
                height: label.offsetHeight
            };
        }).sort(function (left, right) { return left.x - right.x; });
        [0, 1].forEach(function (side) {
            var band = items.filter(function (item, index) {
                return index % 2 === side;
            });
            band.forEach(function (item, index) {
                var previous = index ? band[index - 1] : null;
                var desired = item.x - item.width / 2;
                item.left = Math.max(2, desired, previous
                    ? previous.left + previous.width + 6 : 2);
            });
            for (var index = band.length - 1; index >= 0; index -= 1) {
                var next = band[index + 1];
                var rightEdge = next ? next.left - 6 : mapBox.width - 2;
                band[index].left = Math.max(2, Math.min(
                    band[index].left, rightEdge - band[index].width
                ));
            }
            band.forEach(function (item) {
                item.top = side
                    ? svgBottom + (bandHeight - item.height) / 2
                    : (bandHeight - item.height) / 2;
                item.side = side;
                item.label.style.left = item.left + 'px';
                item.label.style.top = item.top + 'px';
            });
        });
        get('ck-leaders').innerHTML = items.map(function (item) {
            var anchor = Math.max(item.left + 8, Math.min(
                item.left + item.width - 8, item.x
            ));
            var endY = item.side ? item.top : item.top + item.height;
            return '<line data-i="' + item.index
                + '" x1="' + item.x.toFixed(1) + '" y1="'
                + item.y.toFixed(1) + '" x2="' + anchor.toFixed(1)
                + '" y2="' + endY.toFixed(1) + '"/>';
        }).join('');
    }

    function renderMap(date, sun) {
        if (!state.map) return;
        var minute = Math.floor(date / 60000);
        var clocks = pinClocks();
        Array.prototype.forEach.call(get('ck-labels').children,
            function (label, index) {
                label.querySelector('span').textContent = ' '
                    + formatTime(date, clocks[index].timezone, false);
            });
        if (minute === state.lastMapMinute) return;
        state.lastMapMinute = minute;
        placeLabels();
        var antipode = [sun[0] + 180, -sun[1]];
        state.map.svg.querySelector('.ck-night').innerHTML = [90, 84, 78, 72]
            .map(function (radius) {
                return '<path d="' + state.map.path(
                    d3.geoCircle().center(antipode).radius(radius)()
                ) + '"/>';
            }).join('');
        state.map.svg.querySelector('.ck-term').setAttribute('d',
            state.map.path(d3.geoCircle().center(antipode).radius(90)()));
        var sunPoint = state.map.projection(sun);
        state.map.svg.querySelector('.ck-sun').setAttribute('transform',
            'translate(' + sunPoint[0].toFixed(1) + ','
            + sunPoint[1].toFixed(1) + ')');
        var lat = Math.abs(sun[1]).toFixed(1)
            + (sun[1] >= 0 ? '°N' : '°S');
        var lon = Math.abs(sun[0]).toFixed(1)
            + (sun[0] >= 0 ? '°E' : '°W');
        get('ck-map-note').textContent = '☀ Sun overhead: ' + lat + ' ' + lon;
    }

    function setHot(index) {
        Array.prototype.forEach.call(root.querySelectorAll(
            '.ck-pin, .ck-label, .ck-leaders line, .ck-card'
        ), function (element) {
            element.classList.toggle('is-hot', index !== null
                && Number(element.getAttribute('data-i')) === index);
        });
    }

    function renderPlanner(date) {
        var start = dateStart(state.plannerDate);
        var key = state.plannerDate + ':' + state.h12;
        if (state.plannerHour !== key) {
            state.plannerHour = key;
            rows.innerHTML = clockList().map(function (clock) {
                var cells = '';
                for (var index = 0; index < 24; index += 1) {
                    var at = new Date(start);
                    at.setHours(start.getHours() + index);
                    var value = parts(at, clock.timezone);
                    var label = state.h12 ? ((value.h % 12) || 12) : value.h;
                    var suffix = state.h12
                        ? '<small>' + (value.h < 12 ? 'am' : 'pm') + '</small>'
                        : '';
                    var midnight = value.h === 0 && !value.mi
                        ? ' midnight' : '';
                    var title = clock.name + ': '
                        + formatDate(at, clock.timezone, true) + ' '
                        + formatTime(at, clock.timezone, false);
                    cells += '<button type="button" class="ck-cell '
                        + dayStatus(value.h, value.wd) + midnight
                        + '" data-col="' + index + '" title="'
                        + escapeHtml(title) + '">' + label + suffix
                        + '</button>';
                }
                return '<div class="ck-row"><span class="name">'
                    + escapeHtml(clock.name) + '</span>' + cells + '</div>';
            }).join('');
        }
        var selected = Math.floor((date.getTime() - start.getTime()) / 3600000);
        Array.prototype.forEach.call(rows.querySelectorAll('.ck-cell'),
            function (cell) {
                cell.classList.toggle('col-sel',
                    Number(cell.getAttribute('data-col')) === selected);
            });
    }

    function setOffset(minutes) {
        state.offset = Math.max(-1440, Math.min(1440, minutes));
        get('ck-range').value = String(Math.round(state.offset / 15) * 15);
        state.lastMapMinute = null;
        tick();
    }

    function setPlannerDate(key) {
        if (!/^\d{4}-\d{2}-\d{2}$/.test(key)) return;
        var current = new Date();
        var date = key.split('-').map(Number);
        state.plannerDate = key;
        state.baseDate = new Date(
            date[0], date[1] - 1, date[2], current.getHours(),
            current.getMinutes(), current.getSeconds(), current.getMilliseconds()
        ).getTime();
        state.baseRealTime = Date.now();
        state.offset = 0;
        get('ck-range').value = '0';
        state.plannerHour = null;
        state.lastMapMinute = null;
        tick();
    }

    function resetDate() {
        state.plannerDate = dateKey(new Date());
        state.baseDate = null;
        state.baseRealTime = null;
        state.offset = 0;
        get('ck-planner-date').value = state.plannerDate;
        get('ck-range').value = '0';
        state.plannerHour = null;
        state.lastMapMinute = null;
        tick();
    }

    function paintFormat() {
        Array.prototype.forEach.call(root.querySelectorAll('[data-h12]'),
            function (button) {
                var active = (button.getAttribute('data-h12') === '1')
                    === state.h12;
                button.classList.toggle('is-active', active);
                button.setAttribute('aria-pressed', String(active));
            });
    }

    function tick() {
        if (!state.clocks.length) return;
        var date = now();
        var sun = subsolar(date);
        var formatted = formatTime(date, 'LOCAL', true);
        var match = formatted.match(/^(.*\d{2})([:.]\d{2})(.*)$/);
        get('ck-big').innerHTML = match
            ? escapeHtml(match[1]) + '<span class="sec">'
                + escapeHtml(match[2] + match[3]) + '</span>'
            : escapeHtml(formatted);
        get('ck-today').textContent = formatDate(date, 'LOCAL', true);
        get('ck-zone').textContent = localZone.replace(/_/g, ' ')
            + ' (' + utcLabel(offsetOf(date, 'LOCAL')) + ')';
        var output = get('ck-offset');
        var live = state.offset === 0 && state.baseDate === null;
        output.classList.toggle('is-live', live);
        output.textContent = state.offset === 0
            ? (live ? '● Now' : 'Selected date')
            : (state.offset > 0 ? '+' : '−') + formatSpan(state.offset);
        get('ck-reset').hidden = live;
        renderCards(date, sun);
        renderMap(date, sun);
        renderPlanner(date);
    }

    function bind() {
        get('ck-range').addEventListener('input', function (event) {
            setOffset(Number(event.target.value));
        });
        get('ck-planner-date').value = state.plannerDate;
        get('ck-planner-date').addEventListener('change', function (event) {
            setPlannerDate(event.target.value);
        });
        get('ck-reset').addEventListener('click', resetDate);
        root.querySelector('.ck-seg').addEventListener('click',
            function (event) {
                var button = event.target.closest('[data-h12]');
                if (!button) return;
                state.h12 = button.getAttribute('data-h12') === '1';
                try {
                    localStorage.setItem('clock-h12', state.h12 ? '1' : '0');
                } catch (error) {
                    // The format toggle remains usable when storage is disabled.
                }
                formatters = {};
                paintFormat();
                state.plannerHour = null;
                tick();
            });
        grid.addEventListener('mouseover', function (event) {
            var card = event.target.closest('.ck-card');
            if (card) setHot(Number(card.getAttribute('data-i')));
        });
        grid.addEventListener('mouseleave', function () { setHot(null); });
        get('ck-map').addEventListener('mouseover', function (event) {
            var pin = event.target.closest('.ck-pin');
            if (pin) setHot(Number(pin.getAttribute('data-i')));
        });
        get('ck-map').addEventListener('mouseleave', function () {
            setHot(null);
        });
        rows.addEventListener('click', function (event) {
            var cell = event.target.closest('.ck-cell');
            if (!cell) return;
            var target = dateStart(state.plannerDate);
            target.setHours(target.getHours()
                + Number(cell.getAttribute('data-col')));
            var base = state.baseDate === null ? Date.now()
                : state.baseDate + Date.now() - state.baseRealTime;
            state.offset = Math.round((target.getTime() - base) / 60000);
            get('ck-range').value = String(Math.max(-1440,
                Math.min(1440, state.offset)));
            state.lastMapMinute = null;
            tick();
        });
        rows.addEventListener('mouseover', function (event) {
            var cell = event.target.closest('.ck-cell');
            var column = cell && cell.getAttribute('data-col');
            Array.prototype.forEach.call(rows.querySelectorAll('.ck-cell'),
                function (item) {
                    item.classList.toggle('col-hot', column !== null
                        && item.getAttribute('data-col') === column);
                });
        });
        rows.addEventListener('mouseleave', function () {
            Array.prototype.forEach.call(rows.querySelectorAll('.col-hot'),
                function (cell) { cell.classList.remove('col-hot'); });
        });
        window.addEventListener('resize', function () {
            window.requestAnimationFrame(placeLabels);
        });
    }

    function loadClocks() {
        if (!apiUrl) {
            grid.innerHTML = '<p class="ck-state">Clock service is unavailable.</p>';
            return;
        }
        fetch(apiUrl).then(function (response) {
            if (!response.ok) throw new Error('Clock request failed');
            return response.json();
        }).then(function (data) {
            if (!data || !data.success || !Array.isArray(data.clocks)) {
                throw new Error('Invalid clock response');
            }
            state.clocks = data.clocks.map(function (clock) {
                return {
                    name: String(clock.name || ''),
                    timezone: String(clock.timezone || 'UTC')
                };
            }).filter(function (clock) {
                return clock.name && clock.timezone;
            });
            buildCards();
            buildPins();
            tick();
            window.setInterval(tick, 1000);
        }).catch(function () {
            grid.innerHTML = '<p class="ck-state">Failed to load clocks.</p>';
            rows.innerHTML = '';
        });
    }

    paintFormat();
    bind();
    initMap();
    loadClocks();
}());