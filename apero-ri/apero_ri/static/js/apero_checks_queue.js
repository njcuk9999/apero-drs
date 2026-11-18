/* APERO RI - APERO checks queue page */
(function () {
    'use strict';

    if (window.__ARI_APERO_CHECKS_QUEUE_INIT__) return;
    window.__ARI_APERO_CHECKS_QUEUE_INIT__ = true;

    var cfg = window.ARI_APERO_CHECKS_QUEUE || {};
    var pollTimer = null;
    var logRefreshTimer = null;
    var logPauseEnabled = false;
    var currentTaskId = null;
    var currentLogPath = null;
    // Find-in-log state.
    var findState = { matches: [], idx: 0 };
    var currentLogText = '';

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
    /* Log overlay (full-screen, with find/filter)                         */
    /* ------------------------------------------------------------------ */
    function logScrollToMatch(el) {
        var content = document.getElementById('acq-log-content');
        if (!el || !content) return;
        var cr = content.getBoundingClientRect();
        var er = el.getBoundingClientRect();
        content.scrollTop +=
            (er.top - cr.top) - content.clientHeight / 2 + el.clientHeight / 2;
    }

    function resetLogFind() {
        findState.matches = [];
        findState.idx = 0;
        var input = document.getElementById('acq-log-find');
        var count = document.getElementById('acq-log-find-count');
        var content = document.getElementById('acq-log-content');
        if (input) input.value = '';
        if (count) count.textContent = '';
        if (content) {
            content.querySelectorAll('.acq-log-match-line,.acq-log-match-current')
                .forEach(function (el) {
                    el.classList.remove('acq-log-match-line', 'acq-log-match-current');
                });
        }
    }

    function updateLogFind() {
        var content = document.getElementById('acq-log-content');
        var input = document.getElementById('acq-log-find');
        var count = document.getElementById('acq-log-find-count');
        if (!content) return;
        var query = input ? input.value.trim() : '';

        var lines = content.querySelectorAll('.acq-log-line');
        lines.forEach(function (el) {
            el.classList.remove('acq-log-match-line', 'acq-log-match-current');
        });

        if (!query) {
            findState.matches = [];
            findState.idx = 0;
            if (count) count.textContent = '';
            return;
        }

        var lq = query.toLowerCase();
        var matches = [];
        lines.forEach(function (el) {
            if ((el.textContent || '').toLowerCase().indexOf(lq) >= 0) {
                el.classList.add('acq-log-match-line');
                matches.push(el);
            }
        });

        findState.matches = matches;
        findState.idx = 0;

        if (matches.length > 0) {
            matches[0].classList.add('acq-log-match-current');
            logScrollToMatch(matches[0]);
        }

        if (count) {
            count.textContent = matches.length === 0
                ? 'No matches'
                : '1 / ' + matches.length;
        }
    }

    function logFindNav(dir) {
        var matches = findState.matches;
        var count = document.getElementById('acq-log-find-count');
        if (!matches || !matches.length) return;
        matches[findState.idx].classList.remove('acq-log-match-current');
        findState.idx = (findState.idx + dir + matches.length) % matches.length;
        matches[findState.idx].classList.add('acq-log-match-current');
        logScrollToMatch(matches[findState.idx]);
        if (count) {
            count.textContent = (findState.idx + 1) + ' / ' + matches.length;
        }
    }

    function renderLogContent(text) {
        var content = document.getElementById('acq-log-content');
        if (!content) return;
        currentLogText = text;
        if (logPauseEnabled) return;

        var html = '';
        text.split('\n').forEach(function (line, idx) {
            if (!line) return;
            var escaped = esc(line);
            var open = '<span class="acq-log-line" id="acql-' + idx +
                '" data-line="' + idx + '">';
            if (line.indexOf('-!!|') >= 0) {
                html += open + '<span class="acq-log-error">' + escaped + '</span></span>';
            } else if (line.indexOf('-@!|') >= 0) {
                html += open + '<span class="acq-log-warn">' + escaped + '</span></span>';
            } else {
                html += open + escaped + '</span>';
            }
        });
        content.innerHTML = html;
        content.scrollTop = content.scrollHeight;
        resetLogFind();
    }

    function openLogOverlay(filename) {
        var overlay = document.getElementById('acq-log-overlay');
        var nameEl = document.getElementById('acq-log-filename');
        if (!overlay) return;
        if (nameEl) nameEl.textContent = filename || '';
        overlay.classList.add('acq-log-overlay--open');
        document.body.style.overflow = 'hidden';
        logPauseEnabled = false;
        updateLogPauseButton();
        startLogRefreshing();
    }

    function closeLogOverlay() {
        var overlay = document.getElementById('acq-log-overlay');
        if (overlay) overlay.classList.remove('acq-log-overlay--open');
        document.body.style.overflow = '';
        currentLogText = '';
        stopLogRefreshing();
        currentTaskId = null;
        currentLogPath = null;
    }

    function fetchAndShowLog(taskId, logPath) {
        var label = logPath || taskId || '(log)';
        currentTaskId = taskId;
        currentLogPath = logPath;
        openLogOverlay(label);
        var content = document.getElementById('acq-log-content');
        if (content) {
            content.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Loading log&hellip;';
        }
        logRefreshContent();
    }

    function logRefreshContent() {
        var logUrl = String(cfg.taskLogUrl || '');
        if (!logUrl || !currentTaskId) {
            renderLogContent(currentLogPath ? 'Log file: ' + currentLogPath : '(no log available)');
            return;
        }
        var url = logUrl + '?task_id=' + encodeURIComponent(currentTaskId) + '&lines=300';
        getJson(url).then(function (data) {
            renderLogContent(String(data.content || '(empty log)'));
        }).catch(function () {
            renderLogContent(currentLogPath ? 'Log file: ' + currentLogPath : '(could not load log)');
        });
    }

    function updateLogPauseButton() {
        var pauseBtn = document.getElementById('acq-log-pause');
        if (!pauseBtn) return;
        if (logPauseEnabled) {
            pauseBtn.classList.add('ari-btn--active');
            pauseBtn.innerHTML = '<i class="fa-solid fa-play"></i> Resume Refresh';
        } else {
            pauseBtn.classList.remove('ari-btn--active');
            pauseBtn.innerHTML = '<i class="fa-solid fa-pause"></i> Pause Refresh';
        }
    }

    function toggleLogPause() {
        logPauseEnabled = !logPauseEnabled;
        updateLogPauseButton();
        if (!logPauseEnabled) {
            logRefreshContent();
        }
    }

    function startLogRefreshing() {
        if (logRefreshTimer) clearInterval(logRefreshTimer);
        logRefreshTimer = setInterval(logRefreshContent, 1000);
    }

    function stopLogRefreshing() {
        if (logRefreshTimer) {
            clearInterval(logRefreshTimer);
            logRefreshTimer = null;
        }
    }

    function initLogOverlay() {
        var closeBtn = document.getElementById('acq-log-close');
        var backdrop = document.getElementById('acq-log-backdrop');
        var pauseBtn = document.getElementById('acq-log-pause');
        var copyBtn = document.getElementById('acq-log-copy');
        var findInput = document.getElementById('acq-log-find');
        var findPrev = document.getElementById('acq-log-find-prev');
        var findNext = document.getElementById('acq-log-find-next');

        if (closeBtn) closeBtn.addEventListener('click', closeLogOverlay);
        if (backdrop) backdrop.addEventListener('click', closeLogOverlay);
        if (pauseBtn) pauseBtn.addEventListener('click', toggleLogPause);
        if (copyBtn) {
            copyBtn.addEventListener('click', function () {
                if (!navigator.clipboard) return;
                navigator.clipboard.writeText(currentLogText || '');
            });
        }
        if (findInput) {
            findInput.addEventListener('input', updateLogFind);
            findInput.addEventListener('keydown', function (e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    logFindNav(e.shiftKey ? -1 : 1);
                } else if (e.key === 'Escape') {
                    closeLogOverlay();
                }
            });
        }
        if (findPrev) findPrev.addEventListener('click', function () { logFindNav(-1); });
        if (findNext) findNext.addEventListener('click', function () { logFindNav(1); });

        document.addEventListener('keydown', function (e) {
            var overlay = document.getElementById('acq-log-overlay');
            if (!overlay || !overlay.classList.contains('acq-log-overlay--open')) return;
            if (e.key === 'Escape') closeLogOverlay();
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
                        closeLogOverlay();
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
    initLogOverlay();
    refresh();
    startPolling();
})();
