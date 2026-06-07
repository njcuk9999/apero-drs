/* APERO RI - APERO checks queue page */
(function () {
    'use strict';

    if (window.__ARI_APERO_CHECKS_QUEUE_INIT__) return;
    window.__ARI_APERO_CHECKS_QUEUE_INIT__ = true;

    var cfg = window.ARI_APERO_CHECKS_QUEUE || {};
    var pollTimer = null;
    // Track which log is currently expanded (task_id or log_path).
    var _activeLogKey = '';

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

    /* ------------------------------------------------------------------ */
    /* Helpers                                                              */
    /* ------------------------------------------------------------------ */
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
        if (!profileId || !value) return '';
        return '/monitor_portal/apero_checks/'
            + encodeURIComponent(profileId)
            + '/'
            + encodeURIComponent(value);
    }

    function checkHref(obsdir, checkKey) {
        var profileId = String(cfg.profileId || '').trim();
        var night = String(obsdir || '').trim();
        var key = String(checkKey || '').trim();
        if (!profileId || !night) return '';
        if (!key) return obsdirHref(night);
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
        if (!value || !href) return esc(value);
        return '<a href="' + href + '">' + esc(value) + '</a>';
    }

    function linkedCheck(row) {
        var raw = String(row.check_key || '').trim();
        var label = raw || 'all checks';
        var href = checkHref(row.obsdir || '', raw);
        if (!href) {
            return raw ? esc(raw) : '<span class="acq-note">all checks</span>';
        }
        return '<a href="' + href + '">' + esc(label) + '</a>';
    }

    function fmtDuration(seconds) {
        if (seconds == null || seconds === '') return '';
        var s = Number(seconds);
        if (isNaN(s)) return '';
        if (s < 60) return s.toFixed(1) + 's';
        var m = Math.floor(s / 60);
        var rem = (s % 60).toFixed(0);
        return m + 'm ' + rem + 's';
    }

    function getVerbose() {
        var sel = document.getElementById('acq-verbose-select');
        if (!sel) return 1;
        return parseInt(sel.value, 10) || 1;
    }

    function updateLastRefresh() {
        var node = document.getElementById('acq-last-update');
        if (!node) return;
        node.textContent = 'Last update: ' + new Date().toLocaleString();
    }

    /* ------------------------------------------------------------------ */
    /* Log panel                                                            */
    /* ------------------------------------------------------------------ */
    function showLogPanel(key, content) {
        var panel = document.getElementById('acq-log-panel');
        if (!panel) return;
        _activeLogKey = key;
        panel.textContent = content || '(no content)';
        panel.style.display = 'block';
        panel.scrollTop = panel.scrollHeight;
    }

    function hideLogPanel() {
        var panel = document.getElementById('acq-log-panel');
        if (panel) panel.style.display = 'none';
        _activeLogKey = '';
    }

    function fetchAndShowLog(taskId, logPath) {
        // If already showing this task's log, toggle it off.
        var key = taskId || logPath || '';
        if (_activeLogKey === key) {
            hideLogPanel();
            return;
        }
        var logUrl = String(cfg.taskLogUrl || '');
        if (!logUrl || !taskId) {
            // Fallback: show the raw path as text.
            showLogPanel(key, logPath ? 'Log file: ' + logPath : '(no log available)');
            return;
        }
        var url = logUrl + '?task_id=' + encodeURIComponent(taskId) + '&lines=300';
        getJson(url).then(function (data) {
            var text = String(data.content || '(empty log)');
            showLogPanel(key, text);
        }).catch(function () {
            // Fall back to showing path if we can't fetch the content.
            showLogPanel(key, logPath ? 'Log file: ' + logPath : '(could not load log)');
        });
    }

    /* ------------------------------------------------------------------ */
    /* Render functions                                                     */
    /* ------------------------------------------------------------------ */
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
            var logBtn = row.log_path
                ? '<button class="acq-log-btn" data-acq-log-task="' + taskId +
                  '" data-acq-log-path="' + esc(row.log_path) +
                  '" title="View log"><i class="fa-solid fa-file-lines"></i></button>'
                : '';
            return '<tr>' +
                '<td>' + modePill(row) + '</td>' +
                '<td>' + linkedObsdir(row) + '</td>' +
                '<td>' + linkedCheck(row) + '</td>' +
                '<td>' + esc(row.status || '') + '</td>' +
                '<td>' + progress + '</td>' +
                '<td><button class="ari-btn ari-btn--sm ari-btn--secondary" data-acq-cancel="' +
                taskId + '">Cancel</button> ' + logBtn + '</td>' +
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
            tbody.innerHTML = '<tr><td colspan="7" class="acq-empty">No recent manual history for this profile.</td></tr>';
            return;
        }
        tbody.innerHTML = rows.map(function (row) {
            var taskId = esc(row.task_id || '');
            var logPath = String(row.log_path || '');
            var dur = fmtDuration(row.duration_seconds);
            var logBtn = logPath
                ? '<button class="acq-log-btn" data-acq-log-task="' + taskId +
                  '" data-acq-log-path="' + esc(logPath) +
                  '" title="View task log"><i class="fa-solid fa-file-lines"></i> View</button>'
                : '<span class="acq-note">—</span>';
            // Status colour: green pass, red fail/cancelled.
            var status = String(row.status || '');
            var statusHtml = status === 'completed'
                ? '<span style="color:#16a34a;">' + esc(status) + '</span>'
                : (status === 'failed' || status === 'cancelled'
                    ? '<span style="color:#dc2626;">' + esc(status) + '</span>'
                    : esc(status));
            return '<tr>' +
                '<td>' + esc(row.timestamp || '') + '</td>' +
                '<td>' + modePill(row) + '</td>' +
                '<td>' + linkedObsdir(row) + '</td>' +
                '<td>' + linkedCheck(row) + '</td>' +
                '<td>' + statusHtml + '</td>' +
                '<td>' + esc(dur) + '</td>' +
                '<td>' + logBtn + '</td>' +
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

    /* ------------------------------------------------------------------ */
    /* Event delegation                                                     */
    /* ------------------------------------------------------------------ */
    function onTableClick(event) {
        // Cancel button.
        var cancelBtn = event.target.closest('[data-acq-cancel]');
        if (cancelBtn) {
            var taskId = String(cancelBtn.getAttribute('data-acq-cancel') || '');
            if (!taskId) return;
            postJson(String(cfg.cancelUrl || ''), { task_id: taskId })
                .then(refresh)
                .catch(function (err) {
                    window.alert(String(err || 'Could not cancel task.'));
                });
            return;
        }
        // Log viewer button.
        var logBtn = event.target.closest('[data-acq-log-task]');
        if (logBtn) {
            var tid = String(logBtn.getAttribute('data-acq-log-task') || '');
            var lp = String(logBtn.getAttribute('data-acq-log-path') || '');
            fetchAndShowLog(tid, lp);
            return;
        }
    }

    function initButtons() {
        var btnRefresh = document.getElementById('acq-btn-refresh');
        if (btnRefresh) btnRefresh.addEventListener('click', refresh);

        var btnKill = document.getElementById('acq-btn-kill');
        if (btnKill) {
            btnKill.addEventListener('click', function () {
                if (!window.confirm('Kill all APERO check tasks for this profile?')) return;
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
                if (!window.confirm(
                    'Clear all APERO check history for this profile?\n' +
                    '(Only this profile\'s history is affected.)'
                )) return;
                postJson(String(cfg.clearUrl || ''), {})
                    .then(function () {
                        hideLogPanel();
                        return refresh();
                    })
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
