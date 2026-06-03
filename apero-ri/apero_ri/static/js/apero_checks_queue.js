/* APERO RI - APERO checks queue page */
(function () {
    'use strict';

    if (window.__ARI_APERO_CHECKS_QUEUE_INIT__) return;
    window.__ARI_APERO_CHECKS_QUEUE_INIT__ = true;

    var cfg = window.ARI_APERO_CHECKS_QUEUE || {};
    var pollTimer = null;

    function esc(value) {
        return String(value == null ? '' : value)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function postJson(url, payload) {
        return fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload || {}),
        }).then(function (res) {
            return res.json().catch(function () {
                return {};
            }).then(function (data) {
                if (!res.ok || !data.success) {
                    var msg = String(data.error || res.statusText || 'Request failed');
                    throw new Error(msg);
                }
                return data;
            });
        });
    }

    function getJson(url) {
        return fetch(url).then(function (res) {
            return res.json().catch(function () {
                return {};
            }).then(function (data) {
                if (!res.ok || !data.success) {
                    var msg = String(data.error || res.statusText || 'Request failed');
                    throw new Error(msg);
                }
                return data;
            });
        });
    }

    function modePill(row) {
        var mode = String(row.task_mode || '');
        var label = String(row.task_label || mode || 'Unknown');
        var klass = 'acq-pill';
        if (mode === 'full_obsdir') klass += ' acq-pill--night';
        if (mode === 'single_check') klass += ' acq-pill--check';
        return '<span class="' + klass + '">' + esc(label) + '</span>';
    }

    function obsdirHref(obsdir) {
        var profileId = String(cfg.profileId || '').trim();
        var value = String(obsdir || '').trim();
        if (!profileId || !value) {
            return '';
        }
        return '/monitor_portal/apero_checks/'
            + encodeURIComponent(profileId)
            + '/'
            + encodeURIComponent(value);
    }

    function checkHref(obsdir, checkKey) {
        var profileId = String(cfg.profileId || '').trim();
        var night = String(obsdir || '').trim();
        var key = String(checkKey || '').trim();
        if (!profileId || !night) {
            return '';
        }
        if (!key) {
            return obsdirHref(night);
        }
        return '/monitor_portal/apero_checks/'
            + encodeURIComponent(profileId)
            + '/'
            + encodeURIComponent(night)
            + '/check/'
            + encodeURIComponent(key);
    }

    function linkedObsdir(row) {
        var value = String(row.obsdir || '').trim();
        var href = obsdirHref(value);
        if (!value || !href) {
            return esc(value);
        }
        return '<a href="' + href + '">' + esc(value) + '</a>';
    }

    function linkedCheck(row) {
        var raw = String(row.check_key || '').trim();
        var label = raw || 'all checks';
        var href = checkHref(row.obsdir || '', raw);
        if (!href) {
            return raw
                ? esc(raw)
                : '<span class="acq-note">all checks</span>';
        }
        return '<a href="' + href + '">' + esc(label) + '</a>';
    }

    function updateLastRefresh() {
        var node = document.getElementById('acq-last-update');
        if (!node) return;
        node.textContent = 'Last update: ' + new Date().toLocaleString();
    }

    function renderRunning(rows) {
        var tbody = document.querySelector('#acq-running-table tbody');
        if (!tbody) return;
        if (!Array.isArray(rows) || !rows.length) {
            tbody.innerHTML = '<tr><td colspan="6" class="acq-empty">No running tasks.</td></tr>';
            return;
        }
        tbody.innerHTML = rows.map(function (row) {
            var taskId = esc(row.task_id || '');
            var progress = Number(row.progress || 0).toFixed(1) + '%';
            return '<tr>' +
                '<td>' + modePill(row) + '</td>' +
                '<td>' + linkedObsdir(row) + '</td>' +
                '<td>' + linkedCheck(row) + '</td>' +
                '<td>' + esc(row.status || '') + '</td>' +
                '<td>' + progress + '</td>' +
                '<td><button class="ari-btn ari-btn--sm ari-btn--secondary" data-acq-cancel="' +
                taskId + '">Cancel</button></td>' +
                '</tr>';
        }).join('');
    }

    function renderQueued(rows) {
        var tbody = document.querySelector('#acq-queued-table tbody');
        if (!tbody) return;
        if (!Array.isArray(rows) || !rows.length) {
            tbody.innerHTML = '<tr><td colspan="6" class="acq-empty">No queued tasks.</td></tr>';
            return;
        }
        tbody.innerHTML = rows.map(function (row) {
            var taskId = esc(row.task_id || '');
            return '<tr>' +
                '<td>' + esc(row.position || '') + '</td>' +
                '<td>' + modePill(row) + '</td>' +
                '<td>' + linkedObsdir(row) + '</td>' +
                '<td>' + linkedCheck(row) + '</td>' +
                '<td>' + esc(row.status || '') + '</td>' +
                '<td><button class="ari-btn ari-btn--sm ari-btn--secondary" data-acq-cancel="' +
                taskId + '">Cancel</button></td>' +
                '</tr>';
        }).join('');
    }

    function renderHistory(rows) {
        var tbody = document.querySelector('#acq-history-table tbody');
        if (!tbody) return;
        if (!Array.isArray(rows) || !rows.length) {
            tbody.innerHTML = '<tr><td colspan="6" class="acq-empty">No recent manual history for this profile.</td></tr>';
            return;
        }
        tbody.innerHTML = rows.map(function (row) {
            return '<tr>' +
                '<td>' + esc(row.timestamp || '') + '</td>' +
                '<td>' + modePill(row) + '</td>' +
                '<td>' + linkedObsdir(row) + '</td>' +
                '<td>' + linkedCheck(row) + '</td>' +
                '<td>' + esc(row.status || '') + '</td>' +
                '<td>' + esc(row.details || '') + '</td>' +
                '</tr>';
        }).join('');
    }

    function renderAll(data) {
        renderRunning(data.running || []);
        renderQueued(data.queued || []);
        renderHistory(data.history || []);
        updateLastRefresh();
    }

    function refresh() {
        if (!cfg.statusUrl) return Promise.resolve();
        return getJson(String(cfg.statusUrl)).then(renderAll).catch(function (err) {
            window.console.error(err);
        });
    }

    function onTableClick(event) {
        var btn = event.target.closest('[data-acq-cancel]');
        if (!btn) return;
        var taskId = String(btn.getAttribute('data-acq-cancel') || '');
        if (!taskId) return;
        postJson(String(cfg.cancelUrl || ''), { task_id: taskId })
            .then(refresh)
            .catch(function (err) {
                window.alert(String(err || 'Could not cancel task.'));
            });
    }

    function initButtons() {
        var btnRefresh = document.getElementById('acq-btn-refresh');
        if (btnRefresh) btnRefresh.addEventListener('click', refresh);

        var btnKill = document.getElementById('acq-btn-kill');
        if (btnKill) {
            btnKill.addEventListener('click', function () {
                if (!window.confirm('Kill all APERO check tasks for this profile?')) {
                    return;
                }
                postJson(String(cfg.killUrl || ''), {})
                    .then(refresh)
                    .catch(function (err) {
                        window.alert(String(err || 'Could not kill tasks.'));
                    });
            });
        }

        var btnClear = document.getElementById('acq-btn-clear');
        if (btnClear) {
            btnClear.addEventListener('click', function () {
                if (!window.confirm('Clear global async task history?')) {
                    return;
                }
                postJson(String(cfg.clearUrl || ''), {})
                    .then(refresh)
                    .catch(function (err) {
                        window.alert(String(err || 'Could not clear history.'));
                    });
            });
        }

        document.addEventListener('click', onTableClick);
    }

    function startPolling() {
        if (pollTimer) clearInterval(pollTimer);
        pollTimer = setInterval(refresh, 5000);
    }

    initButtons();
    refresh();
    startPolling();
})();
