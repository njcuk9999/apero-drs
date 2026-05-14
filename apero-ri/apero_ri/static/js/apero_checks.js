/* APERO RI – Monitor APERO checks */
(function () {
    'use strict';

    if (!window.ARI) window.ARI = {};
    if (window.__ARI_APERO_CHECKS_INIT__) return;
    window.__ARI_APERO_CHECKS_INIT__ = true;

    var cfg = window.ARI_APERO_CHECKS || {};
    var state = {
        historyRows: [],
        historySort: { key: 'date', dir: 'desc' },
        currentFailure: null,
        currentCard: null,
        pendingAction: '',
        selectedIssue: [],
        ignoredChecks: Array.isArray(cfg.ignoredChecks)
            ? cfg.ignoredChecks.slice() : [],
        browsePath: '',
    };

    function esc(value) {
        return String(value == null ? '' : value)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    function query() {
        return new URLSearchParams(window.location.search || '');
    }

    function refreshUrl(extra) {
        var qs = query();
        Object.keys(extra || {}).forEach(function (key) {
            qs.set(key, extra[key]);
        });
        window.location.search = qs.toString();
    }

    function applyObsdirLiveFilter(pattern) {
        var cards = document.querySelectorAll('#ac-card-list .ac-card');
        if (!cards.length) return;

        var value = String(pattern || '').trim();
        var matcher = null;
        if (value) {
            try {
                matcher = new RegExp(value, 'i');
            } catch (_err) {
                matcher = null;
            }
        }

        cards.forEach(function (card) {
            var obsdir = String(card.getAttribute('data-obsdir') || '');
            var show = true;
            if (value) {
                if (matcher) {
                    show = matcher.test(obsdir);
                } else {
                    show = obsdir.toLowerCase().indexOf(
                        value.toLowerCase()
                    ) >= 0;
                }
            }
            card.style.display = show ? '' : 'none';
        });
    }

    function openOverlay(id) {
        var overlay = document.getElementById(id);
        if (overlay) overlay.hidden = false;
    }

    function closeOverlay(id) {
        var overlay = document.getElementById(id);
        if (overlay) overlay.hidden = true;
    }

    function eventEnabled(value) {
        if (!value || typeof value !== 'object') return false;
        return Object.keys(value).length > 0;
    }

    function renderFailureMeta(card, failureKey, failure) {
        var meta = document.getElementById('ac-failure-meta');
        if (!meta) return;

        var overridden = eventEnabled(failure && failure.override);
        var monitored = eventEnabled(failure && failure.monitor);
        var overrideIcon = overridden
            ? '<i class="fa-solid fa-bell ac-failure-meta-icon--override" ' +
              'title="Overridden"></i>'
            : '';
        var monitorIcon = monitored
            ? '<i class="fa-solid fa-triangle-exclamation ' +
              'ac-failure-meta-icon--monitor" title="Monitored"></i>'
            : '';

        meta.innerHTML =
            '<div class="ac-failure-meta-row"><strong>Obsdir:</strong> ' +
            esc(card && card.obsdir ? card.obsdir : '') + '</div>' +
            '<div class="ac-failure-meta-row"><strong>Type:</strong> ' +
            esc(failure && failure.type ? failure.type : '') + '</div>' +
            '<div class="ac-failure-meta-row"><strong>Test:</strong> ' +
            esc(failureKey || '') + '</div>' +
            '<div class="ac-failure-meta-row"><strong>Overridden:</strong> ' +
            '<span class="ac-failure-meta-state ' +
            (overridden
                ? 'ac-failure-meta-state--true' :
                  'ac-failure-meta-state--false') +
            '">' + (overridden ? 'True' : 'False') + '</span>' +
            overrideIcon + '</div>' +
            '<div class="ac-failure-meta-row"><strong>Monitored:</strong> ' +
            '<span class="ac-failure-meta-state ' +
            (monitored
                ? 'ac-failure-meta-state--true' :
                  'ac-failure-meta-state--false') +
            '">' + (monitored ? 'True' : 'False') + '</span>' +
            monitorIcon + '</div>';
    }

    function setFailureNote(message, isError) {
        var note = document.getElementById('ac-failure-save-note');
        if (!note) return;
        if (!message) {
            note.hidden = true;
            note.textContent = '';
            note.style.borderColor = '';
            note.style.background = '';
            note.style.color = '';
            return;
        }
        note.hidden = false;
        note.textContent = message;
        if (isError) {
            note.style.borderColor = '#fecaca';
            note.style.background = '#fef2f2';
            note.style.color = '#b91c1c';
        } else {
            note.style.borderColor = '';
            note.style.background = '';
            note.style.color = '';
        }
    }

    function toggleCommentEditor(show) {
        var editor = document.getElementById('ac-failure-comment-editor');
        if (!editor) return;
        editor.hidden = !show;
        if (!show) {
            state.pendingAction = '';
        }
        updateCommentBoxState();
    }

    function updateCommentBoxState() {
        var input = document.getElementById('ac-failure-comment');
        if (!input) return;

        var data = state.currentFailure && state.currentFailure.data
            ? state.currentFailure.data : {};
        var hasOverride = eventEnabled(data.override);
        var hasMonitor = eventEnabled(data.monitor);
        var canEdit = !!state.pendingAction;

        input.disabled = !canEdit && !hasOverride && !hasMonitor;
        if (input.disabled) {
            input.placeholder = 'Enable override or monitor to add comment';
        }
    }

    function updateToggleLabels(failure) {
        var overrideLabel = document.getElementById('ac-btn-override-label');
        var monitorLabel = document.getElementById('ac-btn-monitor-label');
        var hasOverride = eventEnabled(failure && failure.override);
        var hasMonitor = eventEnabled(failure && failure.monitor);

        if (overrideLabel) {
            overrideLabel.textContent = hasOverride
                ? 'Override: ON' : 'Override: OFF';
        }
        if (monitorLabel) {
            monitorLabel.textContent = hasMonitor
                ? 'Monitor: ON' : 'Monitor: OFF';
        }
    }

    function renderFailurePath(path) {
        var row = document.getElementById('ac-failure-path');
        if (!row) return;
        var value = String(path || '').trim();
        row.textContent = value
            ? 'Check file: ' + value
            : 'Check file: (unknown path)';
    }

    function openCommentEditor(action) {
        if (!state.currentFailure || !state.currentFailure.data) return;
        var label = document.getElementById('ac-failure-comment-label');
        var saveBtn = document.getElementById('ac-btn-save-comment');
        var input = document.getElementById('ac-failure-comment');
        if (!label || !saveBtn || !input) return;

        var data = state.currentFailure.data || {};
        var existing = '';
        if (action === 'override' && data.override) {
            existing = String(data.override.comment || '');
        }
        if (action === 'monitor' && data.monitor) {
            existing = String(data.monitor.comment || '');
        }

        state.pendingAction = action;
        label.textContent = action === 'override'
            ? 'Override comment' : 'Monitor comment';
        saveBtn.textContent = action === 'override'
            ? 'Save override' : 'Save monitor';
        input.value = existing;
        input.placeholder = action === 'override'
            ? 'Enter override comment' : 'Enter monitor comment';
        toggleCommentEditor(true);
        input.focus();
    }

    function buildFailureIcons(failure) {
        var html = '';
        if (eventEnabled(failure && failure.monitor)) {
            html += '<i class="fa-solid fa-bell ac-i-mon" ' +
                'title="Monitored check"></i>';
        }
        if (eventEnabled(failure && failure.override)) {
            html += '<i class="fa-solid fa-triangle-exclamation ac-i-ovr" ' +
                'title="Overridden marker"></i>';
        }
        return html;
    }

    function updateCardJson(cardJson, failureKey, failure, loaded) {
        var card = cardJson || {};
        var rows = Array.isArray(card.visible_failures)
            ? card.visible_failures.slice() : [];
        var replaced = false;
        rows = rows.map(function (pair) {
            if (!Array.isArray(pair) || pair.length < 2) return pair;
            if (String(pair[0]) !== String(failureKey)) return pair;
            replaced = true;
            return [pair[0], failure];
        });
        if (!replaced) rows.push([failureKey, failure]);
        card.visible_failures = rows;
        if (loaded && Array.isArray(loaded.history)) {
            card.history = loaded.history;
        }
        return card;
    }

    function updateFailureUi(loaded) {
        if (!loaded || !state.currentFailure) return;
        var allFailures = loaded.failures || {};
        var key = state.currentFailure.key;
        var failure = allFailures[key];
        if (!failure) return;

        state.currentFailure.data = failure;
        if (state.currentCard) {
            state.currentCard = updateCardJson(
                state.currentCard, key, failure, loaded
            );
        }

        var title = 'APERO Check information: ' +
            (failure.name || key || '');
        document.getElementById('ac-failure-title').textContent = title;
        renderFailureMeta(state.currentCard || loaded, key, failure);
        document.getElementById('ac-failure-message').textContent =
            failure.message || '';
        updateToggleLabels(failure);
        updateCommentBoxState();
        renderFailurePath(
            loaded.__path__
            || (state.currentCard && state.currentCard.path)
            || ''
        );

        document.querySelectorAll('[data-ac-action="failure"]')
            .forEach(function (btn) {
                var obsdir = btn.getAttribute('data-ac-obsdir') || '';
                var btnKey = btn.getAttribute('data-ac-failure-key') || '';
                if (
                    String(obsdir) !== String(loaded.obsdir || '') ||
                    String(btnKey) !== String(key)
                ) {
                    return;
                }
                btn.setAttribute('data-ac-failure', JSON.stringify(failure));
                var cardData = {};
                try {
                    cardData = JSON.parse(
                        btn.getAttribute('data-ac-card') || '{}'
                    );
                } catch (_err) {
                    cardData = {};
                }
                cardData = updateCardJson(cardData, key, failure, loaded);
                btn.setAttribute('data-ac-card', JSON.stringify(cardData));
                var label = btn.querySelector('.ac-check-pill__label');
                if (label) {
                    label.textContent =
                        (failure.type || '') + ':' + (failure.name || key);
                }
                var icons = btn.querySelector('.ac-check-pill__icons');
                if (icons) {
                    icons.innerHTML = buildFailureIcons(failure);
                }
            });
    }

    function copyText(value) {
        if (navigator.clipboard && window.isSecureContext) {
            return navigator.clipboard.writeText(value);
        }
        return new Promise(function (resolve, reject) {
            var input = document.createElement('textarea');
            input.value = value;
            input.setAttribute('readonly', 'readonly');
            input.style.position = 'fixed';
            input.style.opacity = '0';
            document.body.appendChild(input);
            input.select();
            var ok = false;
            try {
                ok = document.execCommand('copy');
            } catch (_err) {
                ok = false;
            }
            document.body.removeChild(input);
            if (ok) resolve();
            else reject(new Error('Copy failed'));
        });
    }

    function normalizeCheckKey(value) {
        return String(value == null ? '' : value).trim();
    }

    function renderIgnoredChecks() {
        var wrap = document.getElementById('ac-ignored-checks');
        if (!wrap) return;
        if (!state.ignoredChecks.length) {
            wrap.innerHTML = '<div class="ac-manage-help">No ignored checks yet. Use Add check to create one.</div>';
            return;
        }
        wrap.innerHTML = state.ignoredChecks.map(function (item, idx) {
            return '<div class="ac-check-card" data-idx="' + idx + '">' +
                '<div>' +
                '<input class="ac-check-card__input ari-user-search__input" ' +
                'data-ignored-check="1" value="' + esc(item) + '" ' +
                'placeholder="Failure key, for example BAD_CCF">' +
                '<div class="ac-check-card__meta">Hidden from the cards and detail views.</div>' +
                '</div>' +
                '<button type="button" class="ari-btn ari-btn--secondary ari-btn--sm" ' +
                'data-ignored-remove="1" aria-label="Remove ignored check">' +
                '<i class="fa-solid fa-trash"></i>' +
                '</button>' +
                '</div>';
        }).join('');
        wrap.querySelectorAll('[data-ignored-remove="1"]').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var card = btn.closest('[data-idx]');
                if (!card) return;
                var idx = Number(card.getAttribute('data-idx') || '-1');
                if (idx < 0) return;
                state.ignoredChecks.splice(idx, 1);
                renderIgnoredChecks();
            });
        });
        wrap.querySelectorAll('[data-ignored-check="1"]').forEach(function (inp) {
            inp.addEventListener('input', function () {
                var card = inp.closest('[data-idx]');
                if (!card) return;
                var idx = Number(card.getAttribute('data-idx') || '-1');
                if (idx < 0) return;
                state.ignoredChecks[idx] = normalizeCheckKey(inp.value);
            });
        });
    }

    function addIgnoredCheck() {
        state.ignoredChecks.push('');
        renderIgnoredChecks();
    }

    function loadDirectory(path) {
        var url = cfg.browseUrl || '';
        if (!url) return;
        var query = new URLSearchParams();
        if (path) query.set('path', path);
        fetch(url + '?' + query.toString())
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data || !data.success) return;
                state.browsePath = data.path || path || '';
                var pathEl = document.getElementById('ac-browse-path');
                var listEl = document.getElementById('ac-browse-list');
                if (pathEl) pathEl.value = state.browsePath;
                if (!listEl) return;
                var html = '';
                if (data.parent && data.parent !== data.path) {
                    html += '<button type="button" class="ac-dir-browser__row ac-dir-browser__row--up" data-dir-path="' + esc(data.parent) + '">' +
                        '<i class="fa-solid fa-arrow-up"></i>' +
                        '<span>..</span>' +
                        '<span class="ac-dir-browser__path">' + esc(data.parent) + '</span>' +
                        '</button>';
                }
                (data.dirs || []).forEach(function (item) {
                    html += '<button type="button" class="ac-dir-browser__row" data-dir-path="' + esc(item.path) + '">' +
                        '<i class="fa-regular fa-folder"></i>' +
                        '<span>' + esc(item.name) + '</span>' +
                        '<span class="ac-dir-browser__path">' + esc(item.path) + '</span>' +
                        '</button>';
                });
                if (!html) {
                    html = '<div class="ac-manage-help" style="padding:0.8rem;">No subdirectories found.</div>';
                }
                listEl.innerHTML = html;
                listEl.querySelectorAll('[data-dir-path]').forEach(function (btn) {
                    btn.addEventListener('click', function () {
                        loadDirectory(btn.getAttribute('data-dir-path') || '');
                    });
                });
            });
    }

    function openBrowseOverlay() {
        openOverlay('ac-browse-overlay');
        var rootInput = document.getElementById('ac-manage-root');
        loadDirectory((rootInput && rootInput.value) || state.browsePath || '');
    }

    function closeBrowseOverlay() {
        closeOverlay('ac-browse-overlay');
    }

    function openManageOverlay() {
        state.ignoredChecks = Array.isArray(cfg.ignoredChecks)
            ? cfg.ignoredChecks.slice() : [];
        var rootInput = document.getElementById('ac-manage-root');
        if (rootInput && cfg) {
            rootInput.value = rootInput.value || '';
        }
        var preview = document.getElementById('ac-manage-root-preview');
        if (preview && rootInput) {
            preview.textContent = rootInput.value || '';
        }
        renderIgnoredChecks();
        openOverlay('ac-manage-overlay');
    }

    function collectIgnoredChecks() {
        return state.ignoredChecks
            .map(normalizeCheckKey)
            .filter(function (value) { return !!value; })
            .filter(function (value, index, arr) {
                return arr.indexOf(value) === index;
            })
            .sort(function (a, b) {
                return a.toLowerCase().localeCompare(b.toLowerCase());
            });
    }

    function showHistory(card) {
        state.currentCard = card;
        state.historyRows = [];
        var rows = card.history || [];
        rows.forEach(function (row, idx) {
            state.historyRows.push({
                date: row.date || '',
                user: row.user || '',
                source: row.source || '',
                comment: row.comment || '',
                _idx: idx,
            });
        });
        document.getElementById('ac-history-title').textContent =
            'History: ' + (card.obsdir || '');
        renderHistory();
        openOverlay('ac-history-overlay');
    }

    function renderHistory() {
        var tbody = document.querySelector('#ac-history-table tbody');
        if (!tbody) return;
        var search = document.getElementById('ac-history-search');
        var filter = String(search ? search.value : '').trim().toLowerCase();
        var rows = state.historyRows.slice();
        rows.sort(function (a, b) {
            var key = state.historySort.key;
            var av = String(a[key] || '').toLowerCase();
            var bv = String(b[key] || '').toLowerCase();
            if (av < bv) return state.historySort.dir === 'asc' ? -1 : 1;
            if (av > bv) return state.historySort.dir === 'asc' ? 1 : -1;
            return 0;
        });
        if (filter) {
            rows = rows.filter(function (row) {
                return [row.date, row.user, row.source, row.comment]
                    .join(' ')
                    .toLowerCase()
                    .indexOf(filter) >= 0;
            });
        }
        tbody.innerHTML = rows.map(function (row) {
            return '<tr>' +
                '<td>' + esc(row.date) + '</td>' +
                '<td>' + esc(row.user) + '</td>' +
                '<td>' + esc(row.source) + '</td>' +
                '<td>' + esc(row.comment) + '</td>' +
                '</tr>';
        }).join('');
    }

    function showFailure(card, failureKey, failure) {
        state.currentCard = card;
        state.currentFailure = {
            key: failureKey,
            data: failure,
        };
        state.pendingAction = '';
        document.getElementById('ac-failure-title').textContent =
            'APERO Check information: ' +
            (failure.name || failureKey || '');
        renderFailureMeta(card, failureKey, failure || {});
        document.getElementById('ac-failure-message').textContent =
            failure.message || '';
        updateToggleLabels(failure || {});
        renderFailurePath(card && card.path ? card.path : '');
        setFailureNote('', false);
        toggleCommentEditor(false);
        openOverlay('ac-failure-overlay');
    }

    function showIssue(card) {
        state.currentCard = card;
        state.selectedIssue = [];
        document.getElementById('ac-issue-title').textContent =
            'Checks: ' + (card.obsdir || '');
        var wrap = document.getElementById('ac-issue-cards');
        var failures = card.visible_failures || [];
        wrap.innerHTML = failures.map(function (pair) {
            var key = pair[0];
            var failure = pair[1] || {};
            return '<button type="button" class="ac-issue-chip ac-issue-chip--selected"' +
                ' data-failure-key="' + esc(key) + '">' +
                '<i class="fa-solid fa-circle-check"></i>' +
                esc(failure.name || key) + '</button>';
        }).join('');
        state.selectedIssue = failures.map(function (pair) {
            return pair[0];
        });
        wrap.querySelectorAll('.ac-issue-chip').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var key = btn.getAttribute('data-failure-key');
                var idx = state.selectedIssue.indexOf(key);
                if (idx >= 0) {
                    state.selectedIssue.splice(idx, 1);
                    btn.classList.remove('ac-issue-chip--selected');
                    btn.querySelector('i').className =
                        'fa-solid fa-circle-xmark';
                } else {
                    state.selectedIssue.push(key);
                    btn.classList.add('ac-issue-chip--selected');
                    btn.querySelector('i').className =
                        'fa-solid fa-circle-check';
                }
            });
        });
        var reason = document.getElementById('ac-issue-reason');
        if (reason) reason.value = '';
        openOverlay('ac-issue-overlay');
    }

    function postJson(url, payload) {
        return fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        }).then(function (resp) {
            return resp.json().then(function (data) {
                if (!resp.ok || data.success === false) {
                    throw new Error(data.error || 'Request failed');
                }
                return data;
            });
        });
    }

    document.addEventListener('click', function (ev) {
        var btn = ev.target.closest('[data-ac-action]');
        if (!btn) return;
        var action = btn.getAttribute('data-ac-action');
        if (action === 'history') {
            showHistory(JSON.parse(btn.getAttribute('data-ac-card') || '{}'));
        } else if (action === 'failure') {
            showFailure(
                JSON.parse(btn.getAttribute('data-ac-card') || '{}'),
                btn.getAttribute('data-ac-failure-key') || '',
                JSON.parse(btn.getAttribute('data-ac-failure') || '{}')
            );
        } else if (action === 'issue') {
            showIssue(JSON.parse(btn.getAttribute('data-ac-card') || '{}'));
        }
    });

    document.addEventListener('click', function (ev) {
        var close = ev.target.closest('[data-ac-close]');
        if (!close) return;
        var closeKey = String(
            close.getAttribute('data-ac-close') || ''
        ).trim();
        if (!closeKey) return;
        if (closeKey.indexOf('ac-') !== 0) {
            closeKey = 'ac-' + closeKey + '-overlay';
        }
        closeOverlay(closeKey);
    });

    var histSearch = document.getElementById('ac-history-search');
    if (histSearch) {
        histSearch.addEventListener('input', renderHistory);
    }
    document.querySelectorAll('#ac-history-table th[data-ac-sort]')
        .forEach(function (th) {
            th.addEventListener('click', function () {
                var key = th.getAttribute('data-ac-sort');
                if (state.historySort.key === key) {
                    state.historySort.dir =
                        state.historySort.dir === 'asc' ? 'desc' : 'asc';
                } else {
                    state.historySort.key = key;
                    state.historySort.dir = 'asc';
                }
                renderHistory();
            });
        });

    var btnOverride = document.getElementById('ac-btn-override');
    if (btnOverride) {
        btnOverride.addEventListener('click', function () {
            if (!state.currentCard || !state.currentFailure) return;
            if (eventEnabled(state.currentFailure.data.override)) {
                postJson(cfg.apiUpdateUrl, {
                    profile_id: cfg.profileId,
                    obsdir: state.currentCard.obsdir,
                    check_path: state.currentCard.path || '',
                    failure_key: state.currentFailure.key,
                    action: 'clear_override',
                    comment: '',
                }).then(function (data) {
                    updateFailureUi(data.check || {});
                    toggleCommentEditor(false);
                    setFailureNote('Override turned OFF and saved.', false);
                }).catch(function (err) {
                    setFailureNote(String(err || 'Save failed'), true);
                });
                return;
            }
            openCommentEditor('override');
        });
    }

    var btnMonitor = document.getElementById('ac-btn-monitor');
    if (btnMonitor) {
        btnMonitor.addEventListener('click', function () {
            if (!state.currentCard || !state.currentFailure) return;
            if (eventEnabled(state.currentFailure.data.monitor)) {
                postJson(cfg.apiUpdateUrl, {
                    profile_id: cfg.profileId,
                    obsdir: state.currentCard.obsdir,
                    check_path: state.currentCard.path || '',
                    failure_key: state.currentFailure.key,
                    action: 'clear_monitor',
                    comment: '',
                }).then(function (data) {
                    updateFailureUi(data.check || {});
                    toggleCommentEditor(false);
                    setFailureNote('Monitor turned OFF and saved.', false);
                }).catch(function (err) {
                    setFailureNote(String(err || 'Save failed'), true);
                });
                return;
            }
            openCommentEditor('monitor');
        });
    }

    var btnSaveComment = document.getElementById('ac-btn-save-comment');
    if (btnSaveComment) {
        btnSaveComment.addEventListener('click', function () {
            if (!state.currentCard || !state.currentFailure) return;
            var action = state.pendingAction;
            if (action !== 'override' && action !== 'monitor') return;
            var comment = document.getElementById('ac-failure-comment').value;
            postJson(cfg.apiUpdateUrl, {
                profile_id: cfg.profileId,
                obsdir: state.currentCard.obsdir,
                check_path: state.currentCard.path || '',
                failure_key: state.currentFailure.key,
                action: action,
                comment: comment,
            }).then(function (data) {
                updateFailureUi(data.check || {});
                setFailureNote(
                    (action === 'override'
                        ? 'Override saved to YAML.'
                        : 'Monitor saved to YAML.'),
                    false
                );
                toggleCommentEditor(false);
            }).catch(function (err) {
                setFailureNote(String(err || 'Save failed'), true);
            });
        });
    }

    var btnCancelComment = document.getElementById('ac-btn-cancel-comment');
    if (btnCancelComment) {
        btnCancelComment.addEventListener('click', function () {
            toggleCommentEditor(false);
        });
    }

    var btnClear = document.getElementById('ac-btn-clear');
    if (btnClear) {
        btnClear.addEventListener('click', function () {
            if (!state.currentCard || !state.currentFailure) return;
            postJson(cfg.apiUpdateUrl, {
                profile_id: cfg.profileId,
                obsdir: state.currentCard.obsdir,
                check_path: state.currentCard.path || '',
                failure_key: state.currentFailure.key,
                action: 'clear',
                comment: '',
            }).then(function (data) {
                updateFailureUi(data.check || {});
                toggleCommentEditor(false);
                setFailureNote('Override and monitor cleared in YAML.', false);
            }).catch(function (err) {
                setFailureNote(String(err || 'Clear failed'), true);
            });
        });
    }

    var btnCopy = document.getElementById('ac-btn-copy');
    if (btnCopy) {
        btnCopy.addEventListener('click', function () {
            if (!state.currentFailure || !state.currentFailure.data) return;
            var key = state.currentFailure.key || '';
            var failure = state.currentFailure.data || {};
            var title = failure.name || key;
            var obsdir = String(
                (state.currentCard && state.currentCard.obsdir) || ''
            );
            var typeValue = String(failure.type || '');
            var testValue = String(key || '');
            var hasOverride = eventEnabled(failure.override);
            var overrideMsg = hasOverride
                ? String((failure.override || {}).comment || '')
                : '';
            var hasMonitor = eventEnabled(failure.monitor);
            var monitorMsg = hasMonitor
                ? String((failure.monitor || {}).comment || '')
                : '';
            var checkPath = String(
                (state.currentCard && state.currentCard.path) || ''
            );
            var message = String(failure.message || '');
            var divider = '='.repeat(80);
            var payload =
                divider + '\n' +
                title + '\n' +
                divider + '\n' +
                'obsdir: ' + obsdir + '\n' +
                'type: ' + typeValue + '\n' +
                'test: ' + testValue + '\n' +
                'overridden: ' + (hasOverride ? 'True' : 'False') + '\n' +
                'overridden message: ' + overrideMsg + '\n' +
                'monitored: ' + (hasMonitor ? 'True' : 'False') + '\n' +
                'monitored message: ' + monitorMsg + '\n' +
                'check file: ' + checkPath + '\n' +
                divider + '\n' +
                message + '\n' +
                divider;
            copyText(payload).then(function () {
                setFailureNote('Copied report to clipboard.', false);
            }).catch(function () {
                setFailureNote('Could not copy to clipboard.', true);
            });
        });
    }

    var btnCloseFailure = document.getElementById('ac-btn-close');
    if (btnCloseFailure) {
        btnCloseFailure.addEventListener('click', function () {
            toggleCommentEditor(false);
        });
    }

    var btnCreateIssue = document.getElementById('ac-btn-create-issue');
    if (btnCreateIssue) {
        btnCreateIssue.addEventListener('click', function () {
            if (!state.currentCard) return;
            var reason = document.getElementById('ac-issue-reason').value || '';
            postJson(cfg.apiIssueUrl, {
                profile_id: cfg.profileId,
                obsdir: state.currentCard.obsdir,
                failures: state.selectedIssue,
                reason: reason,
                origin_url: window.location.href,
            }).then(function () {
                window.location.reload();
            });
        });
    }

    var btnRefresh = document.getElementById('ac-btn-refresh');
    if (btnRefresh) {
        btnRefresh.addEventListener('click', function () {
            window.location.reload();
        });
    }

    var btnManage = document.getElementById('ac-btn-manage');
    if (btnManage) {
        btnManage.addEventListener('click', function () {
            openManageOverlay();
        });
    }

    var btnAddIgnored = document.getElementById('ac-btn-add-ignored');
    if (btnAddIgnored) {
        btnAddIgnored.addEventListener('click', function () {
            addIgnoredCheck();
        });
    }

    var btnBrowseRoot = document.getElementById('ac-btn-browse-root');
    if (btnBrowseRoot) {
        btnBrowseRoot.addEventListener('click', function () {
            openBrowseOverlay();
        });
    }

    var btnSave = document.getElementById('ac-btn-save-config');
    if (btnSave) {
        btnSave.addEventListener('click', function () {
            var root = document.getElementById('ac-manage-root').value || '';
            var ignored = collectIgnoredChecks();
            postJson(cfg.apiConfigUrl, {
                checks_root: root,
                ignored_checks: ignored,
            }).then(function () {
                cfg.ignoredChecks = ignored.slice();
                window.location.reload();
            });
        });
    }

    var btnOverridden = document.getElementById('ac-btn-overridden');
    if (btnOverridden) {
        btnOverridden.addEventListener('click', function () {
            refreshUrl({
                show_overridden: query().get('show_overridden') === '1' ? '0' : '1',
            });
        });
    }

    var btnMonitored = document.getElementById('ac-btn-monitored');
    if (btnMonitored) {
        btnMonitored.addEventListener('click', function () {
            refreshUrl({
                show_monitored: query().get('show_monitored') === '1' ? '0' : '1',
            });
        });
    }

    var typeSel = document.getElementById('ac-type');
    if (typeSel) {
        typeSel.addEventListener('change', function () {
            refreshUrl({ type: typeSel.value });
        });
    }

    var obsdirFilter = document.getElementById('ac-obsdir-filter');
    if (obsdirFilter) {
        applyObsdirLiveFilter(obsdirFilter.value || '');
        obsdirFilter.addEventListener('input', function () {
            applyObsdirLiveFilter(obsdirFilter.value || '');
        });
    }

    var obsdirSort = document.getElementById('ac-obsdir-sort');
    if (obsdirSort) {
        obsdirSort.addEventListener('change', function () {
            refreshUrl({
                obsdir_sort: obsdirSort.value || 'desc',
                page: '1',
            });
        });
    }

    var perSel = document.getElementById('ac-perpage');
    if (perSel) {
        perSel.addEventListener('change', function () {
            refreshUrl({ per_page: perSel.value, page: '1' });
        });
    }

    var rootInput = document.getElementById('ac-manage-root');
    if (rootInput) {
        rootInput.addEventListener('input', function () {
            var preview = document.getElementById('ac-manage-root-preview');
            if (preview) preview.textContent = rootInput.value || '';
        });
    }

    var browseClose = document.querySelector('[data-ac-close="browse"]');
    if (browseClose) {
        browseClose.addEventListener('click', closeBrowseOverlay);
    }

    var browseGo = document.getElementById('ac-browse-go');
    var browseUp = document.getElementById('ac-browse-up');
    var browseSelect = document.getElementById('ac-browse-select');
    var browsePath = document.getElementById('ac-browse-path');
    if (browseGo && browsePath) {
        browseGo.addEventListener('click', function () {
            loadDirectory(browsePath.value || '');
        });
    }
    if (browseUp && browsePath) {
        browseUp.addEventListener('click', function () {
            var value = String(browsePath.value || '').replace(/\/+$/, '');
            if (!value) return;
            var parts = value.split('/');
            parts.pop();
            loadDirectory(parts.join('/') || '/');
        });
    }
    if (browseSelect && browsePath) {
        browseSelect.addEventListener('click', function () {
            var rootInput = document.getElementById('ac-manage-root');
            if (rootInput) {
                rootInput.value = browsePath.value || '';
                var preview = document.getElementById('ac-manage-root-preview');
                if (preview) preview.textContent = rootInput.value;
            }
            closeBrowseOverlay();
        });
    }

    var manageOverlay = document.getElementById('ac-manage-overlay');
    if (manageOverlay) {
        manageOverlay.addEventListener('click', function (ev) {
            if (ev.target === manageOverlay) {
                closeOverlay('ac-manage-overlay');
            }
        });
    }

    var browseOverlay = document.getElementById('ac-browse-overlay');
    if (browseOverlay) {
        browseOverlay.addEventListener('click', function (ev) {
            if (ev.target === browseOverlay) {
                closeBrowseOverlay();
            }
        });
    }
}());
