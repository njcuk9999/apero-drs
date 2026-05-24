(function () {
    'use strict';

    var cfg = window.ARI_NAV_CLOCKS || {};
    var apiUrl = String(cfg.apiUrl || '');

    var wrap = document.getElementById('ari-clock-wrap');
    var panel = document.getElementById('ari-clock-panel');
    var list = document.getElementById('ari-clock-list');
    var link = document.getElementById('ari-clock-link');

    var state = {
        clocks: [
            {name: 'UTC', timezone: 'UTC', locked: true},
            {name: 'Local', timezone: 'LOCAL', locked: true},
        ],
        timer: null,
        loaded: false,
    };

    function esc(text) {
        var d = document.createElement('div');
        d.textContent = String(text || '');
        return d.innerHTML;
    }

    function formatTime(date, timezone) {
        var tz = timezone === 'LOCAL' ? undefined : timezone;
        var parts = new Intl.DateTimeFormat('en-CA', {
            timeZone: tz,
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false,
        }).formatToParts(date);
        var out = {};
        parts.forEach(function (p) { out[p.type] = p.value; });
        return out.year + '-' + out.month + '-' + out.day + ' '
            + out.hour + ':' + out.minute + ':' + out.second;
    }

    function render() {
        if (!list) return;
        var now = new Date();
        if (!state.clocks.length) {
            list.innerHTML = '<div class="ari-clock-item">No clocks configured.</div>';
            return;
        }
        var html = '';
        var maxNameLen = 5;
        state.clocks.forEach(function (row) {
            var labelLen = String((row || {}).name || '').length + 2;
            if (labelLen > maxNameLen) {
                maxNameLen = labelLen;
            }
        });
        maxNameLen = Math.max(6, Math.min(maxNameLen, 22));
        list.style.setProperty('--ari-clock-name-ch', String(maxNameLen) + 'ch');
        state.clocks.forEach(function (row) {
            var name = String((row || {}).name || '');
            var timezone = String((row || {}).timezone || 'UTC');
            var when = formatTime(now, timezone);
            html += '<div class="ari-clock-item">'
                + '<span class="ari-clock-item__name">'
                + esc('[' + name + ']')
                + '</span>'
                + '<span class="ari-clock-item__time">'
                + esc(when)
                + '</span>'
                + '</div>';
        });
        list.innerHTML = html;
    }

    function stopTick() {
        if (state.timer !== null) {
            window.clearInterval(state.timer);
            state.timer = null;
        }
    }

    function startTick() {
        render();
        if (state.timer !== null) return;
        state.timer = window.setInterval(render, 1000);
    }

    function openPanel() {
        if (!wrap) return;
        wrap.classList.add('ari-clock-wrap--open');
        startTick();
    }

    function closePanel() {
        if (!wrap) return;
        wrap.classList.remove('ari-clock-wrap--open');
        stopTick();
    }

    function load() {
        if (!apiUrl || state.loaded) return;
        state.loaded = true;
        fetch(apiUrl)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (data && data.success && Array.isArray(data.clocks)) {
                    state.clocks = data.clocks;
                }
                render();
            })
            .catch(function () {
                render();
            });
    }

    function bind() {
        if (!wrap || !panel || !list) return;

        wrap.addEventListener('mouseenter', function () {
            load();
            openPanel();
        });
        wrap.addEventListener('mouseleave', function () {
            closePanel();
        });

        if (link) {
            link.addEventListener('focus', function () {
                load();
                openPanel();
            });
            link.addEventListener('blur', function () {
                closePanel();
            });
        }
    }

    bind();
}());
