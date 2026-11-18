/*
 * APERO RI - astrometrics "Unresolved objects" tab.
 *
 * Loads the raw object names the ASTROM check could not resolve (for the
 * user's instruments) from /api/astrometrics/unresolved the first time the
 * tab is opened, renders them, filters them, and sends a name to the
 * Resolve target tab via window.AriAstroResolveName.
 */
(function () {
    'use strict';

    var panel = document.getElementById('astro-tab-unresolved');
    if (!panel) return;
    var tbody = document.getElementById('aun-tbody');
    var filterInput = document.getElementById('aun-filter');
    var summary = document.getElementById('aun-summary');
    var countBadge = document.getElementById('aun-count');
    var notice = document.getElementById('aun-notice');
    var refreshBtn = document.getElementById('aun-refresh');
    // Translated labels from the template.
    var text = {
        loading: panel.dataset.aunLoading || '',
        empty: panel.dataset.aunEmpty || '',
        error: panel.dataset.aunError || '',
        count: panel.dataset.aunCount || '{n}',
        resolvedSince: panel.dataset.aunResolvedSince || '{n}',
        stale: panel.dataset.aunStale || '{n}',
        more: panel.dataset.aunMore || '(+{n})',
        resolve: panel.dataset.aunResolve || 'Resolve'
    };
    var loaded = false;

    function esc(value) {
        return String(value == null ? '' : value)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function fill(template, n) {
        return String(template).replace('{n}', String(n));
    }

    function messageRow(message) {
        tbody.innerHTML = '<tr><td colspan="6" class="aun-empty">'
            + esc(message) + '</td></tr>';
    }

    // Build one table row (searchable text kept in a data attribute).
    function rowHtml(row) {
        var nights = (row.night_links || []).map(function (night) {
            return '<a href="' + esc(night.url) + '" title="'
                + esc(night.profile_id) + '">' + esc(night.obsdir) + '</a>';
        }).join(', ');
        var hidden = Number(row.n_nights || 0)
            - (row.night_links || []).length;
        if (hidden > 0) {
            nights += ' <span class="aun-note">'
                + esc(fill(text.more, hidden)) + '</span>';
        }
        var search = [row.name].concat(row.instruments || [],
            row.profiles || [],
            (row.night_links || []).map(function (n) { return n.obsdir; }))
            .join(' ').toLowerCase();
        var keys = (row.header_keys || []).join(', ');
        var files = (row.files || []).join(', ');
        return '<tr data-aun-search="' + esc(search) + '">'
            + '<td><div class="aun-name">' + esc(row.name) + '</div>'
            + (keys ? '<div class="aun-sub">' + esc(keys) + '</div>' : '')
            + '</td>'
            + '<td>' + esc((row.instruments || []).join(', ')) + '</td>'
            + '<td>' + nights + '</td>'
            + '<td>' + esc(row.n_files)
            + (files ? '<div class="aun-sub">' + esc(files) + '</div>' : '')
            + '</td>'
            + '<td class="aun-sub">' + esc(row.resolver) + '</td>'
            + '<td><button type="button"'
            + ' class="ari-btn ari-btn--sm ari-btn--primary aun-resolve-btn"'
            + ' data-aun-name="' + esc(row.name) + '">'
            + '<i class="fa-solid fa-magnifying-glass-location"></i> '
            + esc(text.resolve) + '</button></td>'
            + '</tr>';
    }

    function render(data) {
        var rows = data.rows || [];
        if (countBadge) countBadge.textContent = String(rows.length);
        var parts = [fill(text.count, rows.length)];
        if (data.n_resolved_since) {
            parts.push(fill(text.resolvedSince, data.n_resolved_since));
        }
        if (summary) summary.textContent = parts.join(' · ');
        var stale = (data.nights_without_details || []).length;
        if (notice) {
            notice.hidden = stale === 0;
            notice.textContent = stale ? fill(text.stale, stale) : '';
        }
        if (!rows.length) {
            messageRow(text.empty);
            return;
        }
        tbody.innerHTML = rows.map(rowHtml).join('');
        applyFilter();
    }

    function load() {
        loaded = true;
        messageRow(text.loading);
        fetch(panel.dataset.aunUrl, { credentials: 'same-origin' })
            .then(function (resp) {
                return resp.json().then(function (data) {
                    if (!resp.ok || !data.success) {
                        throw new Error(data.error || text.error);
                    }
                    return data;
                });
            })
            .then(render)
            .catch(function (err) {
                messageRow((err && err.message) || text.error);
            });
    }

    function applyFilter() {
        var query = filterInput ? filterInput.value.trim().toLowerCase() : '';
        tbody.querySelectorAll('tr[data-aun-search]').forEach(function (tr) {
            var haystack = tr.getAttribute('data-aun-search') || '';
            tr.hidden = query !== '' && haystack.indexOf(query) < 0;
        });
    }

    // Load the first time the tab is opened.
    var tabButton = document.querySelector('.ari-htab[data-htab="unresolved"]');
    if (tabButton) {
        tabButton.addEventListener('click', function () {
            if (!loaded) load();
        });
    }
    if (refreshBtn) refreshBtn.addEventListener('click', load);
    if (filterInput) filterInput.addEventListener('input', applyFilter);
    // Resolve: switch to the Resolve target tab and look the name up.
    tbody.addEventListener('click', function (event) {
        var button = event.target.closest('[data-aun-name]');
        if (!button || typeof window.AriAstroResolveName !== 'function') {
            return;
        }
        window.AriAstroResolveName(button.getAttribute('data-aun-name'),
                                   true);
    });
})();
