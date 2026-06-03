(function () {
    'use strict';

    var cfg = window.ARI_CLOCK_PAGE || {};
    var apiUrl = String(cfg.apiUrl || '');
    var bodyEl = document.getElementById('clock-table-body');
    var state = { clocks: [], timer: null };

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

    function offsetMinutes(date, timezone) {
        if (timezone === 'LOCAL') {
            return -date.getTimezoneOffset();
        }
        var dtf = new Intl.DateTimeFormat('en-US', {
            timeZone: timezone,
            hour12: false,
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
        });
        var map = {};
        dtf.formatToParts(date).forEach(function (p) { map[p.type] = p.value; });
        var asUtc = Date.UTC(
            parseInt(map.year, 10),
            parseInt(map.month, 10) - 1,
            parseInt(map.day, 10),
            parseInt(map.hour, 10),
            parseInt(map.minute, 10),
            parseInt(map.second, 10)
        );
        return Math.round((asUtc - date.getTime()) / 60000);
    }

    function formatOffset(minutes) {
        if (!isFinite(minutes)) return '';
        if (minutes === 0) return '+0';
        var sign = minutes > 0 ? '+' : '-';
        var abs = Math.abs(minutes);
        var hh = Math.floor(abs / 60);
        var mm = abs % 60;
        if (mm === 0) return sign + String(hh);
        return sign + String(hh) + ':' + String(mm).padStart(2, '0');
    }

    function renderRows() {
        if (!bodyEl) return;
        if (!state.clocks.length) {
            bodyEl.innerHTML = '<tr class="ot-row">'
                + '<td colspan="3" class="ot-cell ot-empty">'
                + 'No clocks configured.'
                + '</td></tr>';
            return;
        }
        var now = new Date();
        var html = '';
        state.clocks.forEach(function (row) {
            var name = String((row || {}).name || '');
            var timezone = String((row || {}).timezone || 'UTC');
            var when = formatTime(now, timezone);
            var diff = formatOffset(offsetMinutes(now, timezone));
            html += '<tr class="ot-row">'
                + '<td class="ot-cell">' + esc(name) + '</td>'
                + '<td class="ot-cell">' + esc(when) + '</td>'
                + '<td class="ot-cell">' + esc(diff) + '</td>'
                + '</tr>';
        });
        bodyEl.innerHTML = html;
    }

    function startTimer() {
        if (state.timer !== null) return;
        state.timer = window.setInterval(renderRows, 1000);
    }

    function load() {
        if (!apiUrl || !bodyEl) return;
        fetch(apiUrl)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data || !data.success) {
                    bodyEl.innerHTML = '<tr class="ot-row">'
                        + '<td colspan="3" class="ot-cell ot-error">'
                        + 'Failed to load clocks.'
                        + '</td></tr>';
                    return;
                }
                state.clocks = Array.isArray(data.clocks) ? data.clocks : [];
                renderRows();
                startTimer();
            })
            .catch(function () {
                bodyEl.innerHTML = '<tr class="ot-row">'
                    + '<td colspan="3" class="ot-cell ot-error">'
                    + 'Failed to load clocks.'
                    + '</td></tr>';
            });
    }

    load();
}());
