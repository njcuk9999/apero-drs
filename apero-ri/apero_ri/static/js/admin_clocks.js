(function () {
    'use strict';

    var cfg = window.ARI_ADMIN_CLOCKS || {};
    var apiUrl = String(cfg.apiUrl || '');

    var addBtn = document.getElementById('clock-add');
    var saveBtn = document.getElementById('clock-save');
    var statusEl = document.getElementById('clock-status');
    var bodyEl = document.getElementById('clock-admin-body');

    var state = {
        rows: [],
        timezones: [],
    };

    function loadTimezoneOptions() {
        var values = [];
        if (
            typeof Intl !== 'undefined'
            && typeof Intl.supportedValuesOf === 'function'
        ) {
            try {
                values = Intl.supportedValuesOf('timeZone') || [];
            } catch (err) {
                values = [];
            }
        }
        if (!Array.isArray(values) || !values.length) {
            values = [
                'Africa/Casablanca',
                'America/Chicago',
                'America/Los_Angeles',
                'America/Montreal',
                'America/New_York',
                'America/Phoenix',
                'America/Sao_Paulo',
                'Asia/Kolkata',
                'Asia/Seoul',
                'Asia/Shanghai',
                'Asia/Tokyo',
                'Australia/Sydney',
                'Europe/London',
                'Europe/Paris',
                'Europe/Zurich',
                'Pacific/Auckland',
                'UTC',
            ];
        }
        values = values
            .map(function (item) { return String(item || '').trim(); })
            .filter(Boolean);
        if (values.indexOf('UTC') === -1) {
            values.push('UTC');
        }
        values.sort();
        state.timezones = values;
    }

    function timezoneSelectHtml(idx, timezone, locked) {
        var current = String(timezone || 'UTC');
        var html = '';
        var options = state.timezones.slice();
        if (current === 'LOCAL' && options.indexOf('LOCAL') === -1) {
            options.unshift('LOCAL');
        }
        if (options.indexOf(current) === -1) {
            options.unshift(current);
        }
        html += '<select class="ari-input ari-input--sm" '
            + 'data-role="timezone" data-idx="' + idx + '" '
            + (locked ? 'disabled' : '') + '>';
        options.forEach(function (tz) {
            html += '<option value="' + esc(tz) + '"'
                + (tz === current ? ' selected' : '') + '>'
                + esc(tz) + '</option>';
        });
        html += '</select>';
        return html;
    }

    function esc(text) {
        var d = document.createElement('div');
        d.textContent = String(text || '');
        return d.innerHTML;
    }

    function setStatus(text, isError) {
        if (!statusEl) return;
        statusEl.textContent = String(text || '');
        statusEl.style.color = isError ? '#a54528' : '#4f613b';
    }

    function formatTime(date, timezone) {
        var tz = timezone === 'LOCAL' ? undefined : timezone;
        var parts = new Intl.DateTimeFormat('en-CA', {
            timeZone: tz,
            year: 'numeric', month: '2-digit', day: '2-digit',
            hour: '2-digit', minute: '2-digit', second: '2-digit',
            hour12: false,
        }).formatToParts(date);
        var out = {};
        parts.forEach(function (p) { out[p.type] = p.value; });
        return out.year + '-' + out.month + '-' + out.day + ' '
            + out.hour + ':' + out.minute + ':' + out.second;
    }

    function moveRow(idx, delta) {
        var target = idx + delta;
        if (idx < 2 || target < 2 || target >= state.rows.length) return;
        var tmp = state.rows[idx];
        state.rows[idx] = state.rows[target];
        state.rows[target] = tmp;
        render();
    }

    function removeRow(idx) {
        if (idx < 2) return;
        state.rows.splice(idx, 1);
        render();
    }

    function render() {
        if (!bodyEl) return;
        if (!state.rows.length) {
            bodyEl.innerHTML = '<tr><td colspan="4" class="at-muted-hint">No clocks.</td></tr>';
            return;
        }
        var now = new Date();
        var html = '';
        state.rows.forEach(function (row, idx) {
            var locked = !!row.locked;
            html += '<tr>'
                + '<td><input class="ari-input ari-input--sm" data-role="name" data-idx="' + idx + '"'
                + ' value="' + esc(row.name) + '" ' + (locked ? 'disabled' : '') + '></td>'
                + '<td>' + timezoneSelectHtml(idx, row.timezone, locked) + '</td>'
                + '<td>' + esc('[' + row.name + '] ' + formatTime(now, row.timezone || 'UTC')) + '</td>'
                + '<td>'
                + '<button class="ari-btn ari-btn--secondary" data-role="up" data-idx="' + idx + '" '
                + ((idx <= 2) ? 'disabled' : '') + '>Up</button> '
                + '<button class="ari-btn ari-btn--secondary" data-role="down" data-idx="' + idx + '" '
                + ((idx < 2 || idx >= state.rows.length - 1) ? 'disabled' : '') + '>Down</button> '
                + '<button class="ari-btn ari-btn--secondary" data-role="remove" data-idx="' + idx + '" '
                + (locked ? 'disabled' : '') + '>Remove</button>'
                + '</td>'
                + '</tr>';
        });
        bodyEl.innerHTML = html;
    }

    function bindBodyEvents() {
        if (!bodyEl) return;
        bodyEl.addEventListener('input', function (event) {
            var target = event.target;
            if (!(target instanceof HTMLElement)) return;
            var role = target.getAttribute('data-role');
            var idx = parseInt(target.getAttribute('data-idx') || '-1', 10);
            if (!role || idx < 0 || idx >= state.rows.length) return;
            if (role === 'name') state.rows[idx].name = String(target.value || '');
            if (role === 'timezone') state.rows[idx].timezone = String(target.value || '');
            setStatus('', false);
        });
        bodyEl.addEventListener('change', function (event) {
            var target = event.target;
            if (!(target instanceof HTMLElement)) return;
            var role = target.getAttribute('data-role');
            var idx = parseInt(target.getAttribute('data-idx') || '-1', 10);
            if (!role || idx < 0 || idx >= state.rows.length) return;
            if (role === 'timezone') {
                state.rows[idx].timezone = String(target.value || '');
                render();
            }
            setStatus('', false);
        });
        bodyEl.addEventListener('click', function (event) {
            var target = event.target;
            if (!(target instanceof HTMLElement)) return;
            var btn = target.closest('button[data-role]');
            if (!btn) return;
            var role = btn.getAttribute('data-role');
            var idx = parseInt(btn.getAttribute('data-idx') || '-1', 10);
            if (idx < 0) return;
            if (role === 'up') moveRow(idx, -1);
            if (role === 'down') moveRow(idx, 1);
            if (role === 'remove') removeRow(idx);
        });
    }

    function load() {
        if (!apiUrl || !bodyEl) return;
        fetch(apiUrl)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data || !data.success) {
                    setStatus('Failed to load clocks.', true);
                    return;
                }
                state.rows = Array.isArray(data.clocks) ? data.clocks : [];
                render();
            })
            .catch(function () {
                setStatus('Failed to load clocks.', true);
            });
    }

    function save() {
        if (!apiUrl) return;
        fetch(apiUrl, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({clocks: state.rows}),
        })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data || !data.success) {
                    setStatus(String((data && data.error) || 'Failed to save.'), true);
                    return;
                }
                state.rows = Array.isArray(data.clocks) ? data.clocks : [];
                render();
                setStatus('Saved.', false);
            })
            .catch(function () {
                setStatus('Failed to save clocks.', true);
            });
    }

    if (addBtn) {
        addBtn.addEventListener('click', function () {
            state.rows.push({name: 'New Clock', timezone: 'Europe/Paris', locked: false});
            render();
        });
    }
    if (saveBtn) {
        saveBtn.addEventListener('click', save);
    }

    loadTimezoneOptions();
    bindBodyEvents();
    load();
}());
