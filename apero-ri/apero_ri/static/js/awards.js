(function () {
    'use strict';

    var labels = JSON.parse(document.getElementById('aw-labels').textContent);
    var allRows = JSON.parse(document.getElementById('aw-data').textContent);

    function escapeHtml(value) {
        return String(value == null ? '' : value)
            .replace(/&/g, '&amp;').replace(/</g, '&lt;')
            .replace(/>/g, '&gt;').replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function metric(row, kind, instrument) {
        if (kind === 'instrument') {
            return Number((row.instruments || {})[instrument] || 0);
        }
        if (kind === 'service') return Number(row.total_hours || 0);
        if (kind === 'activity') return Number(row.active_days || 0);
        return Number(row['download_' + kind] || 0);
    }

    function formatMetric(value, kind) {
        if (kind === 'instrument' || kind === 'service') {
            return value.toLocaleString(undefined, {
                minimumFractionDigits: 2, maximumFractionDigits: 2
            });
        }
        if (kind !== 'bytes') return value.toLocaleString();
        var units = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB'];
        var unit = 0;
        while (value >= 1024 && unit < units.length - 1) {
            value /= 1024;
            unit += 1;
        }
        return value.toLocaleString(undefined, {maximumFractionDigits: 2}) +
            ' ' + units[unit];
    }

    function medalIcon(medal, title) {
        if (['gold', 'silver', 'bronze'].indexOf(medal) === -1) return '';
        var description = title + ' - ' + labels[medal];
        return '<i class="fa-solid fa-medal upu-medal upu-medal--' + medal +
            '" role="img" aria-label="' + escapeHtml(description) +
            '" title="' + escapeHtml(description) + '"></i>';
    }

    document.querySelectorAll('.aw-board, .acc-stat').forEach(function (board) {
        var kind = board.dataset.awKind;
        var instrument = board.dataset.awInstrument;
        var metricLabel = kind === 'instrument' || kind === 'service' ?
            labels.hours : kind === 'activity' ? labels.active_days : labels[kind];
        var eligible = allRows.filter(function (row) {
            return metric(row, kind, instrument) > 0 ||
                (kind === 'service' && Number(row.issues_resolved || 0) > 0);
        });
        eligible.sort(function (left, right) {
            return metric(right, kind, instrument) - metric(left, kind, instrument) ||
                String(left.username).localeCompare(String(right.username));
        });
        var self = allRows.find(function (row) { return row.is_self; });
        if (board.classList.contains('acc-stat')) {
            var selfRank = eligible.indexOf(self);
            var value = self ? metric(self, kind, instrument) : 0;
            var medal = self ? (kind === 'instrument' ?
                (self.instrument_medals || {})[instrument] :
                kind === 'service' ? self.service_medal :
                kind === 'activity' ? self.activity_medal :
                (self.download_medals || {})[kind]) : null;
            board.querySelector('.acc-stat-value').innerHTML =
                escapeHtml(formatMetric(value, kind)) + medalIcon(medal, metricLabel);
            board.querySelector('.acc-stat-rank').textContent = selfRank < 0 ?
                labels.unranked : labels.rank + ' #' + (selfRank + 1);
            if (kind === 'service') {
                board.querySelector('.acc-stat-secondary').innerHTML =
                    escapeHtml(labels.issues) + ': ' +
                    Number(self && self.issues_resolved || 0).toLocaleString() +
                    medalIcon(self && self.issues_medal, labels.issues);
            }
            return;
        }
        var selected = eligible.slice(0, 10).map(function (row, index) {
            return {row: row, rank: index + 1};
        });
        if (self && !selected.some(function (item) { return item.row === self; })) {
            var selfRank = eligible.indexOf(self);
            selected.push({row: self, rank: selfRank < 0 ? null : selfRank + 1});
        }

        var list = board.querySelector('.aw-list');
        if (!selected.length) {
            list.innerHTML = '<li class="aw-empty">' + escapeHtml(labels.empty) + '</li>';
            return;
        }
        list.innerHTML = selected.map(function (item) {
            var row = item.row;
            var value = metric(row, kind, instrument);
            var medal = kind === 'instrument' ? (row.instrument_medals || {})[instrument] :
                kind === 'service' ? row.service_medal :
                kind === 'activity' ? row.activity_medal : (row.download_medals || {})[kind];
            var className = 'aw-entry' + (item.rank === 1 ? ' aw-entry--first' : '') +
                (row.is_self ? ' aw-entry--self' : '') +
                (item.rank > 10 || item.rank === null ? ' aw-entry--outside' : '');
            var rank = item.rank === null ? '&mdash;' : String(item.rank);
            var secondary = kind === 'service' ?
                '<span class="aw-secondary">' + escapeHtml(labels.issues) + ': ' +
                Number(row.issues_resolved || 0).toLocaleString() +
                medalIcon(row.issues_medal, labels.issues) + '</span>' : '';
            return '<li class="' + className + '">' +
                '<span class="aw-rank">' + rank + '</span>' +
                '<span class="aw-person"><a class="ari-user-link aw-name" ' +
                'data-username="' + escapeHtml(row.username) + '" href="/user_portal/users/' +
                encodeURIComponent(row.username) + '">' + escapeHtml(row.who) + '</a>' +
                '<span class="aw-username">@' + escapeHtml(row.username) + '</span></span>' +
                '<span class="aw-result"><span class="aw-value">' +
                escapeHtml(formatMetric(value, kind)) + medalIcon(medal, metricLabel) +
                '</span><span class="aw-metric">' + escapeHtml(metricLabel) +
                '</span>' + secondary + '</span></li>';
        }).join('');
    });
})();
