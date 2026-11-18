/*
 * APERO checks: debug-log viewer.
 *
 * Shared by the obsdir page (all checks for one night) and the check page
 * (one check only). The page passes element ids, the API url and the
 * request payload; this module loads the log each time the overlay opens
 * (logs change after re-runs) and provides search, copy and download.
 */
(function (global) {
    'use strict';

    // Escape text before inserting highlight markup.
    function escapeHtml(text) {
        return String(text).replace(/[&<>"']/g, function (charValue) {
            return {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#39;'
            }[charValue];
        });
    }

    // Wire one debug-log button to its overlay.
    function init(opts) {
        var byId = function (key) {
            return document.getElementById(opts.ids[key]);
        };
        var button = byId('button');
        var overlay = byId('overlay');
        var content = byId('content');
        var meta = byId('meta');
        var search = byId('search');
        var matchCount = byId('count');
        var copyBtn = byId('copy');
        var downloadBtn = byId('download');
        var reloadBtn = byId('reload');
        if (!button || !overlay || !content) return;
        var text = opts.text || {};
        // Raw log text of the last successful load.
        var raw = '';

        // Show the log, highlighting the current search term.
        function render() {
            var query = search ? search.value.trim() : '';
            if (!query) {
                content.textContent = raw;
                if (matchCount) matchCount.textContent = '';
                return;
            }
            var pattern = new RegExp(
                query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'),
                'gi'
            );
            var found = 0;
            content.innerHTML = escapeHtml(raw).replace(
                pattern,
                function (matchValue) {
                    found += 1;
                    return '<mark class="ac-yaml-mark">'
                        + matchValue + '</mark>';
                }
            );
            if (matchCount) {
                matchCount.textContent = found
                    ? String(found) + ' ' + (text.matches || 'matches')
                    : (text.noMatch || 'No match');
            }
        }

        // Fetch the log from the API and render it.
        function load() {
            raw = '';
            content.textContent = text.loading || 'Loading...';
            if (meta) meta.textContent = '';
            fetch(opts.url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(opts.payload || {}),
            }).then(function (resp) {
                return resp.json().then(function (data) {
                    if (!resp.ok || data.success === false) {
                        throw new Error(data.error || text.error || '');
                    }
                    return data;
                });
            }).then(function (data) {
                raw = String(data.content || '');
                if (meta) {
                    meta.textContent = String(data.path || '')
                        + ' | ' + (text.updated || 'updated') + ' '
                        + String(data.updated || '');
                }
                render();
            }).catch(function (err) {
                content.textContent = String(
                    (err && err.message) || err || text.error || ''
                );
            });
        }

        // Close the overlay.
        function close() {
            overlay.hidden = true;
        }

        button.addEventListener('click', function () {
            overlay.hidden = false;
            load();
        });
        overlay.querySelectorAll('[data-ac-close]').forEach(function (el) {
            el.addEventListener('click', close);
        });
        document.addEventListener('keydown', function (event) {
            if (event.key === 'Escape' && !overlay.hidden) close();
        });
        if (search) search.addEventListener('input', render);
        if (reloadBtn) reloadBtn.addEventListener('click', load);
        if (copyBtn) {
            copyBtn.addEventListener('click', function () {
                if (!raw) return;
                navigator.clipboard.writeText(raw).catch(function () {});
            });
        }
        if (downloadBtn) {
            downloadBtn.addEventListener('click', function () {
                if (!raw) return;
                var blob = new Blob([raw], { type: 'text/plain' });
                var link = document.createElement('a');
                link.href = URL.createObjectURL(blob);
                link.download = opts.filename || 'apero_check_debug.txt';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                URL.revokeObjectURL(link.href);
            });
        }
    }

    global.AperoChecksDebugLog = { init: init };
})(window);
