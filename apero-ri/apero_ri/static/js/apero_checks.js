/* APERO RI – Monitor APERO checks */
(function () {
    'use strict';

    if (!window.ARI) window.ARI = {};
    if (window.__ARI_APERO_CHECKS_INIT__) return;
    window.__ARI_APERO_CHECKS_INIT__ = true;

    var cfg = window.ARI_APERO_CHECKS || {};
    var state = {
        page: Number(cfg.page || 1),
        perPage: Number(cfg.perPage || 10),
        totalPages: Number(cfg.totalPages || 1),
        totalCards: Number(cfg.totalCards || 0),
        typeFilter: String(cfg.typeFilter || 'all'),
        resultFilter: String(cfg.resultFilter || 'all'),
        obsdirFilter: String(cfg.obsdirFilter || ''),
        obsdirSort: String(cfg.obsdirSort || 'desc'),
        showOverridden: !!cfg.showOverridden,
        showMonitored: !!cfg.showMonitored,
        showPassed: !!cfg.showPassed,
        showTests: false,
        cardsByPage: {},
        filterTimer: null,
        historyRows: [],
        historySort: { key: 'date', dir: 'desc' },
        currentFailure: null,
        currentFailureKind: 'failure',
        currentCard: null,
        pendingAction: '',
        selectedIssue: [],
        ignoredChecks: Array.isArray(cfg.ignoredChecks)
            ? cfg.ignoredChecks.slice() : [],
        overrideAllowed: Array.isArray(cfg.overrideAllowed)
            ? cfg.overrideAllowed.slice() : [],
        browsePath: '',
        canManage: !!cfg.canManage,
        advancedMode: false,
        yamlRawText: '',
        yamlPath: '',
        yamlLastRun: '',
        currentObsdirCard: null,
        reopenObsdirOnRefresh: '',
    };

    function esc(value) {
        return String(value == null ? '' : value)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function escRegex(value) {
        return String(value || '').replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    function query() {
        return new URLSearchParams(window.location.search || '');
    }

    function refreshUrl(extra) {
        var qs = query();
        Object.keys(extra || {}).forEach(function (key) {
            qs.set(key, extra[key]);
        });
        var next = qs.toString();
        var nextUrl = window.location.pathname + (next ? '?' + next : '');
        window.history.replaceState({}, '', nextUrl);
        syncStateFromQuery();
        syncToggleButtons();
        return loadAndRender(state.page, true);
    }

    function boolQuery(value) {
        return value ? '1' : '0';
    }

    function syncStateFromQuery() {
        var qs = query();
        var page = parseInt(qs.get('page') || String(cfg.page || 1), 10);
        var perPage = parseInt(
            qs.get('per_page') || String(cfg.perPage || 10),
            10
        );
        state.page = isNaN(page) ? 1 : Math.max(1, page);
        state.perPage = isNaN(perPage) ? 10 : Math.max(1, perPage);
        state.typeFilter = String(
            qs.get('type') || cfg.typeFilter || 'all'
        );
        state.resultFilter = String(
            qs.get('result_filter') || cfg.resultFilter || 'all'
        );
        state.obsdirFilter = String(
            qs.get('obsdir_filter') || cfg.obsdirFilter || ''
        );
        state.obsdirSort = String(
            qs.get('obsdir_sort') || cfg.obsdirSort || 'desc'
        );
        state.showOverridden =
            String(
                qs.get('show_overridden')
                || boolQuery(cfg.showOverridden)
            ) === '1';
        state.showMonitored =
            String(
                qs.get('show_monitored')
                || boolQuery(cfg.showMonitored)
            ) === '1';
        state.showPassed =
            String(
                qs.get('show_passed')
                || boolQuery(cfg.showPassed)
            ) === '1';
    }

    function buildPageApiUrl(page, pagesToLoad) {
        var qs = new URLSearchParams();
        qs.set('page', String(page || 1));
        qs.set('per_page', String(state.perPage || 10));
        qs.set('type', state.typeFilter || 'all');
        qs.set('result_filter', state.resultFilter || 'all');
        qs.set('obsdir_filter', state.obsdirFilter || '');
        qs.set('obsdir_sort', state.obsdirSort || 'desc');
        qs.set('show_overridden', boolQuery(state.showOverridden));
        qs.set('show_monitored', boolQuery(state.showMonitored));
        qs.set('show_passed', boolQuery(state.showPassed));
        qs.set('pages', String(pagesToLoad || 2));
        return String(cfg.pageApiUrl || '') + '?' + qs.toString();
    }

    function syncToggleButtons() {
        var btnOverridden = document.getElementById('ac-btn-overridden');
        var btnMonitored = document.getElementById('ac-btn-monitored');
        var btnPassed = document.getElementById('ac-btn-passed');
        var btnShowTests = document.getElementById('ac-btn-show-tests');
        var typeSel = document.getElementById('ac-type');
        var resultSel = document.getElementById('ac-result-filter');
        var obsdirFilter = document.getElementById('ac-obsdir-filter');
        var obsdirSort = document.getElementById('ac-obsdir-sort');

        if (btnOverridden) {
            btnOverridden.classList.toggle(
                'ac-toggle-override-on',
                state.showOverridden
            );
            btnOverridden.innerHTML = state.showOverridden
                ? '<i class="fa-solid fa-layer-group"></i>' +
                  ' Hide overridden checks'
                : '<i class="fa-solid fa-layer-group"></i>' +
                  ' Show overridden checks';
        }
        if (btnMonitored) {
            btnMonitored.classList.toggle(
                'ac-toggle-monitor-on',
                state.showMonitored
            );
            btnMonitored.innerHTML = state.showMonitored
                ? '<i class="fa-solid fa-bell-concierge"></i>' +
                  ' Hide monitored checks'
                : '<i class="fa-solid fa-bell-concierge"></i>' +
                  ' Show monitored checks';
        }
        if (btnPassed) {
            btnPassed.classList.toggle(
                'ac-toggle-pass-on',
                state.showPassed
            );
            btnPassed.innerHTML = state.showPassed
                ? '<i class="fa-solid fa-check"></i> Hide passed checks'
                : '<i class="fa-solid fa-check"></i> Show passed checks';
        }
        if (btnShowTests) {
            btnShowTests.classList.toggle(
                'ac-toggle-tests-on',
                !!state.showTests
            );
            btnShowTests.innerHTML = state.showTests
                ? '<i class="fa-solid fa-vial"></i> Hide tests'
                : '<i class="fa-solid fa-vial"></i> Show tests';
        }
        if (typeSel) typeSel.value = state.typeFilter;
        if (resultSel) resultSel.value = state.resultFilter || 'all';
        if (obsdirFilter) obsdirFilter.value = state.obsdirFilter;
        if (obsdirSort) obsdirSort.value = state.obsdirSort;
    }

    function renderPageControls() {
        var infoText = 'Page ' + state.page + ' of ' + state.totalPages;
        ['ac-page-info', 'ac-page-info-top', 'ac-page-info-bottom']
            .forEach(function (id) {
                var el = document.getElementById(id);
                if (el) el.textContent = infoText;
            });
        ['ac-page-prev-top', 'ac-page-prev-bottom']
            .forEach(function (id) {
                var btn = document.getElementById(id);
                if (btn) btn.disabled = state.page <= 1;
            });
        ['ac-page-next-top', 'ac-page-next-bottom']
            .forEach(function (id) {
                var btn = document.getElementById(id);
                if (btn) btn.disabled = state.page >= state.totalPages;
            });
        var select = document.getElementById('ac-page-select');
        if (!select) return;
        var html = '';
        for (var page = 1; page <= state.totalPages; page++) {
            html += '<option value="' + page + '"' +
                (page === state.page ? ' selected' : '') + '>' +
                'Page ' + page + ' of ' + state.totalPages +
                '</option>';
        }
        select.innerHTML = html;
    }

    function jsonAttr(value) {
        return esc(JSON.stringify(value || {}));
    }

    function renderCards(cards) {
        var list = document.getElementById('ac-card-list');
        if (!list) return;
        var rows = Array.isArray(cards) ? cards : [];
        if (!rows.length) {
            list.innerHTML = '<article class="ac-card">' +
                '<div class="ac-card__row">' +
                '<span class="ac-check-empty">No matching YAML files</span>' +
                '</div></article>';
            return;
        }
        list.innerHTML = rows.map(function (card) {
            var failures = Array.isArray(card.visible_failures)
                ? card.visible_failures : [];
            var passes = Array.isArray(card.visible_passes)
                ? card.visible_passes : [];
            var cardJson = jsonAttr(card);
            var html = '<article class="ac-card ac-card--' +
                esc(card.status || 'ok') + '" data-obsdir="' +
                esc(card.obsdir || '') + '" data-ac-card="' +
                cardJson + '"><div class="ac-card__row">';
            html += '<span class="ac-card__row-status" title="Card status">';
            html += card.status === 'ok'
                ? '<i class="fa-solid fa-check ac-i-ok"></i>'
                : '<i class="fa-solid fa-xmark ac-i-bad"></i>';
            html += '</span>';
            html += '<div class="ac-card__date" title="Obsdir: ' +
                esc(card.obsdir || '') + '">' +
                '<div>' + esc(card.obsdir || '') + '</div>' +
                '<div class="ac-card__lastrun">Last run: ' +
                esc(card.last_run || 'n/a') + '</div>' +
                '</div>';
            html += '<div class="ac-card__checks ac-card__checks-main">';
            failures.forEach(function (pair) {
                var key = pair[0];
                var failure = pair[1] || {};
                html += '<button class="ac-check-pill ac-check-pill--failed"' +
                    ' data-ac-action="failure"' +
                    ' data-ac-failure="' + jsonAttr(failure) + '"' +
                    ' data-ac-failure-key="' + esc(key || '') + '"' +
                    ' data-ac-obsdir="' + esc(card.obsdir || '') + '"' +
                    ' data-ac-card="' + cardJson + '">';
                html += '<span class="ac-check-pill__icons ' +
                    'ac-check-pill__icons--start">' +
                    '<i class="fa-solid fa-xmark ac-i-bad" ' +
                    'title="Failed check"></i></span>';
                html += '<span class="ac-check-pill__label">' +
                    esc((failure.type || '') + ':' +
                    (failure.name || key || '')) + '</span>';
                html += '<span class="ac-check-pill__icons">';
                if (eventEnabled(failure.monitor)) {
                    html += '<i class="fa-solid fa-bell ac-i-mon" ' +
                        'title="Monitored check"></i>';
                }
                if (eventEnabled(failure.override)) {
                    html += '<i class="fa-solid fa-triangle-exclamation ' +
                        'ac-i-ovr" title="Overridden marker"></i>';
                }
                html += '</span></button>';
            });
            if (state.showPassed) {
                passes.forEach(function (pair) {
                    var key = pair[0];
                    var passed = pair[1] || {};
                    html += '<button class="ac-check-pill ' +
                        'ac-check-pill--passed" data-ac-action="pass"' +
                        ' data-ac-pass="' + jsonAttr(passed) + '"' +
                        ' data-ac-pass-key="' + esc(key || '') + '"' +
                        ' data-ac-obsdir="' + esc(card.obsdir || '') + '"' +
                        ' data-ac-card="' + cardJson + '">';
                    html += '<span class="ac-check-pill__icons ' +
                        'ac-check-pill__icons--start">' +
                        '<i class="fa-solid fa-check ac-i-pass" ' +
                        'title="Passed check"></i></span>';
                    html += '<span class="ac-check-pill__label">' +
                        esc((passed.type || '') + ':' +
                        (passed.name || key || '')) + '</span>';
                    html += '<span class="ac-check-pill__icons"></span>';
                    html += '</button>';
                });
            }
            if (!failures.length && (!state.showPassed || !passes.length)) {
                html += '<span class="ac-check-empty">No visible checks</span>';
            }
            html += '</div>';
            html += '<div class="ac-card__actions">';
            html += '<button class="ari-btn ari-btn--sm ari-btn--secondary"' +
                ' data-ac-action="rerun-night" data-ac-obsdir="' +
                esc(card.obsdir || '') + '" data-ac-card="' + cardJson + '"' +
                ' title="Re-run APERO checks for this night">' +
                '<i class="fa-solid fa-rotate-right"></i></button>';
            html += '<button class="ari-btn ari-btn--sm ari-btn--secondary"' +
                ' data-ac-action="history" data-ac-obsdir="' +
                esc(card.obsdir || '') + '" data-ac-card="' + cardJson + '"' +
                ' title="Open history">' +
                '<i class="fa-solid fa-clock-rotate-left"></i></button>';
            html += '<button class="ari-btn ari-btn--sm ari-btn--secondary"' +
                ' data-ac-action="issue" data-ac-obsdir="' +
                esc(card.obsdir || '') + '" data-ac-card="' + cardJson + '"' +
                ' title="Create issue">' +
                '<i class="fa-solid fa-flag"></i></button>';
            if (state.canManage) {
                html += '<button class="ari-btn ari-btn--sm ac-btn-danger ' +
                    'ac-delete-only" data-ac-action="delete-night" ' +
                    'data-ac-obsdir="' + esc(card.obsdir || '') + '" ' +
                    'data-ac-card="' + cardJson + '" ' +
                    'title="Delete this night YAML file">' +
                    '<i class="fa-solid fa-trash"></i></button>';
            }
            html += '</div></div></article>';
            return html;
        }).join('');
        syncAdvancedModeUi();
        syncShowTestsUi();
    }

    function syncShowTestsUi() {
        var body = document.body;
        if (!body) return;
        body.classList.toggle('ac-hide-tests', !state.showTests);
    }

    function syncAdvancedModeUi() {
        var body = document.body;
        if (body) {
            body.classList.toggle('ac-delete-mode', !!state.advancedMode);
        }
        var btn = document.getElementById('ac-btn-advanced');
        if (!btn) return;
        if (state.advancedMode) {
            btn.classList.add('ac-btn-danger');
            btn.innerHTML =
                '<i class="fa-solid fa-sliders"></i> Advanced options: ON';
        } else {
            btn.classList.remove('ac-btn-danger');
            btn.innerHTML =
                '<i class="fa-solid fa-sliders"></i> Advanced options';
        }
    }

    function cardForObsdir(obsdir) {
        var target = String(obsdir || '').trim();
        if (!target) return null;
        var cards = state.cardsByPage[String(state.page)] || [];
        for (var idx = 0; idx < cards.length; idx += 1) {
            var card = cards[idx] || {};
            if (String(card.obsdir || '').trim() === target) {
                return card;
            }
        }
        return null;
    }

    function waitForRerunCompletion(obsdir, baselineLastRun, onUpdated) {
        var baseline = String(baselineLastRun || '').trim();
        var tries = 0;
        var maxTries = 24;

        function tick() {
            tries += 1;
            state.cardsByPage = {};
            loadAndRender(state.page, true).then(function () {
                var card = cardForObsdir(obsdir);
                var latest = String(
                    card && card.last_run ? card.last_run : ''
                ).trim();
                if (latest && latest !== baseline) {
                    if (typeof onUpdated === 'function') {
                        onUpdated(latest);
                    }
                    return;
                }
                if (tries >= maxTries) {
                    return;
                }
                window.setTimeout(tick, 5000);
            }).catch(function () {
                if (tries >= maxTries) {
                    return;
                }
                window.setTimeout(tick, 5000);
            });
        }

        window.setTimeout(tick, 5000);
    }

    function requestRerunNight(card) {
        if (!card || !card.obsdir) return;
        var baseline = String(card.last_run || '').trim();
        postJson(cfg.apiRerunNightUrl, {
            profile_id: cfg.profileId,
            obsdir: card.obsdir,
            check_path: card.path || '',
        }).then(function (data) {
            var taskId = String(data.task_id || '').trim();
            if (taskId) {
                window.alert('Night queued (task: ' + taskId + ').');
            } else {
                window.alert('Night queued.');
            }
            waitForRerunCompletion(card.obsdir, baseline, function (latest) {
                window.alert('Night re-run finished. Last run: ' + latest);
                window.setTimeout(function () {
                    window.location.reload();
                }, 700);
            });
        }).catch(function (err) {
            window.alert(String(err || 'Could not queue this night.'));
        });
    }

    function requestDeleteNight(card) {
        if (!card || !card.obsdir) return;
        if (!state.canManage) return;
        var path = String(card.path || '').trim() || card.obsdir;
        if (!window.confirm('This will remove ' + path)) {
            return;
        }
        postJson(cfg.apiDeleteObsdirUrl, {
            profile_id: cfg.profileId,
            obsdir: card.obsdir,
            check_path: card.path || '',
        }).then(function () {
            window.location.reload();
        }).catch(function (err) {
            window.alert(String(err || 'Could not delete this YAML file.'));
        });
    }

    function storePagePayload(data) {
        state.totalPages = Number(data.total_pages || 1);
        state.totalCards = Number(data.total_cards || 0);
        Object.keys(data.pages || {}).forEach(function (key) {
            state.cardsByPage[String(key)] = data.pages[key] || [];
        });
    }

    function fetchPageWindow(page) {
        return fetch(buildPageApiUrl(page, 2))
            .then(function (resp) { return resp.json(); })
            .then(function (data) {
                if (!data || data.success === false) {
                    throw new Error((data && data.error) || 'Load failed');
                }
                storePagePayload(data);
                return data;
            });
    }

    function loadAndRender(page, forceReload) {
        var targetPage = Math.max(1, Number(page || 1));
        state.page = targetPage;
        if (!forceReload && state.cardsByPage[String(targetPage)]) {
            renderCards(state.cardsByPage[String(targetPage)] || []);
            renderPageControls();
            if (!state.cardsByPage[String(targetPage + 1)] &&
                targetPage < state.totalPages) {
                fetchPageWindow(targetPage).catch(function () {});
            }
            return Promise.resolve();
        }
        return fetchPageWindow(targetPage).then(function () {
            renderCards(state.cardsByPage[String(targetPage)] || []);
            renderPageControls();
        }).catch(function (err) {
            var list = document.getElementById('ac-card-list');
            if (list) {
                list.innerHTML = '<article class="ac-card">' +
                    '<div class="ac-card__row">' +
                    '<span class="ac-check-empty">' +
                    esc(String(err || 'Load failed')) +
                    '</span></div></article>';
            }
        });
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
        var keys = ['date', 'user', 'source', 'comment'];
        for (var i = 0; i < keys.length; i += 1) {
            var key = keys[i];
            if (String(value[key] || '').trim()) {
                return true;
            }
        }
        for (var prop in value) {
            if (!Object.prototype.hasOwnProperty.call(value, prop)) continue;
            if (keys.indexOf(prop) >= 0) continue;
            if (String(value[prop] || '').trim()) {
                return true;
            }
        }
        return false;
    }

    function renderFailureMeta(card, failureKey, failure, kind) {
        var meta = document.getElementById('ac-failure-meta');
        if (!meta) return;

        var isPassed = kind === 'pass';
        var overridden = eventEnabled(failure && failure.override);
        var monitored = eventEnabled(failure && failure.monitor);
        var lastRun = '';
        if (failure && failure.last_run) {
            lastRun = String(failure.last_run || '').trim();
        }
        if (!lastRun && card && card.last_run) {
            lastRun = String(card.last_run || '').trim();
        }
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
            '<div class="ac-failure-meta-row"><strong>Result:</strong> ' +
            '<span class="ac-failure-meta-state ' +
            (isPassed
                ? 'ac-failure-meta-state--true' :
                  'ac-failure-meta-state--false') +
            '">' + (isPassed ? 'Passed' : 'Failed') + '</span></div>' +
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
                        monitorIcon + '</div>' +
                        '<div class="ac-failure-meta-row"><strong>Last run:</strong> ' +
                        esc(lastRun || 'n/a') + '</div>';
    }

    function renderFailureHeader(failureKey, failure, kind) {
        var titleEl = document.getElementById('ac-failure-title');
        if (!titleEl) return;

        var header = titleEl.closest('.ac-overlay__header');
        var isPassed = kind === 'pass';
        var iconClass = isPassed ? 'fa-check' : 'fa-xmark';
        var stateClass = isPassed
            ? 'ac-overlay__header--pass'
            : 'ac-overlay__header--failure';
        var name = failure && failure.name ? failure.name : failureKey || '';

        if (header) {
            header.classList.remove(
                'ac-overlay__header--pass',
                'ac-overlay__header--failure'
            );
            header.classList.add(stateClass);
        }

        titleEl.innerHTML =
            '<span class="ac-overlay__title-state">' +
            '<span class="ac-overlay__title-icon">' +
            '<i class="fa-solid ' + iconClass + '"></i>' +
            '</span>' +
            '<span>APERO Check information: ' + esc(name) + '</span>' +
            '</span>';
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
        var isPassed = state.currentFailureKind === 'pass';

        input.disabled = isPassed || (!canEdit && !hasOverride && !hasMonitor);
        if (input.disabled) {
            input.placeholder = isPassed
                ? 'Passed checks are read-only'
                : 'Enable override or monitor to add comment';
        }
    }

    function updateToggleLabels(failure, kind) {
        var overrideLabel = document.getElementById('ac-btn-override-label');
        var monitorLabel = document.getElementById('ac-btn-monitor-label');
        var clearBtn = document.getElementById('ac-btn-clear');
        var hasOverride = eventEnabled(failure && failure.override);
        var hasMonitor = eventEnabled(failure && failure.monitor);
        var isPassed = kind === 'pass';

        if (overrideLabel) {
            overrideLabel.textContent = isPassed
                ? 'Override: N/A'
                : (hasOverride ? 'Override: ON' : 'Override: OFF');
        }
        if (monitorLabel) {
            monitorLabel.textContent = isPassed
                ? 'Monitor: N/A'
                : (hasMonitor ? 'Monitor: ON' : 'Monitor: OFF');
        }
        if (clearBtn) {
            clearBtn.disabled = isPassed;
        }
    }

    function isOverrideAllowed(failureKey) {
        if (!failureKey) return false;
        return state.overrideAllowed.indexOf(String(failureKey)) >= 0;
    }

    function applyOverridePolicy(failureKey, kind) {
        var btn = document.getElementById('ac-btn-override');
        var label = document.getElementById('ac-btn-override-label');
        if (!btn || !label) return;
        if (kind === 'pass') {
            btn.disabled = true;
            label.textContent = 'Override: N/A';
            btn.setAttribute('title', 'Passed checks cannot be overridden');
            return;
        }
        var allowed = isOverrideAllowed(failureKey);
        btn.disabled = !allowed;
        if (allowed) {
            btn.removeAttribute('title');
            return;
        }
        label.textContent = 'Override: DISABLED';
        btn.setAttribute(
            'title',
            'Override is disabled by global policy for this check'
        );
    }

    function _docSlugFromCheckKey(checkKey) {
        var key = String(checkKey || '').trim().toLowerCase();
        if (!key) return '';
        return key;
    }

    function renderFailurePath(path) {
        var row = document.getElementById('ac-failure-path');
        if (!row) return;
        var value = String(path || '').trim();
        row.textContent = value
            ? 'Check file: ' + value
            : 'Check file: (unknown path)';
    }

    function renderFailureDocLink(checkKey, testName) {
        var row = document.getElementById('ac-failure-doc-link');
        if (!row) return;
        var slug = _docSlugFromCheckKey(checkKey);
        if (!slug) {
            row.hidden = true;
            row.innerHTML = '';
            return;
        }
        var docUrl = '/docs/monitor/checks/' + encodeURIComponent(slug);
        var label = String(testName || checkKey || 'this test');
        row.innerHTML =
            '<a class="ari-btn ari-btn--primary" ' +
            'style="font-weight:700; width:100%; text-align:center;" ' +
            'href="' + esc(docUrl) + '" target="_blank" ' +
            'rel="noopener noreferrer">' +
            'Quick link to documentation on ' + esc(label) +
            '</a>';
        row.hidden = false;
    }

    function renderYamlText() {
        var pre = document.getElementById('ac-yaml-content');
        var search = document.getElementById('ac-yaml-search');
        var count = document.getElementById('ac-yaml-match-count');
        if (!pre) return;
        var raw = String(state.yamlRawText || '');
        var term = String(search && search.value ? search.value : '').trim();
        if (!term) {
            pre.textContent = raw;
            if (count) count.textContent = '';
            return;
        }
        var regex = null;
        try {
            regex = new RegExp(escRegex(term), 'gi');
        } catch (_err) {
            regex = null;
        }
        if (!regex) {
            pre.textContent = raw;
            if (count) count.textContent = 'Invalid search pattern';
            return;
        }
        var matches = raw.match(regex);
        var html = esc(raw).replace(
            new RegExp(escRegex(term), 'gi'),
            function (match) {
                return '<mark class="ac-yaml-mark">' + esc(match) + '</mark>';
            }
        );
        pre.innerHTML = html;
        if (count) {
            count.textContent = String((matches || []).length) + ' matches';
        }
    }

    function openYamlViewer() {
        if (!state.currentCard) return;
        var title = document.getElementById('ac-yaml-title');
        var count = document.getElementById('ac-yaml-match-count');
        var search = document.getElementById('ac-yaml-search');
        var pre = document.getElementById('ac-yaml-content');
        if (pre) {
            pre.textContent = 'Loading YAML...';
        }
        if (title) {
            title.textContent = 'Check YAML view';
        }
        if (count) {
            count.textContent = '';
        }
        if (search) {
            search.value = '';
        }
        openOverlay('ac-yaml-overlay');
        postJson(cfg.apiViewYamlUrl, {
            profile_id: cfg.profileId,
            obsdir: state.currentCard.obsdir,
            check_path: state.currentCard.path || '',
        }).then(function (data) {
            state.yamlRawText = String(data.content || '');
            state.yamlPath = String(data.path || '');
            state.yamlLastRun = String(data.last_run || '');
            if (title) {
                title.textContent = 'Check YAML view: ' + state.yamlPath;
                if (state.yamlLastRun) {
                    title.textContent +=
                        ' (last run: ' + state.yamlLastRun + ')';
                }
            }
            renderYamlText();
        }).catch(function (err) {
            state.yamlRawText = '';
            if (pre) {
                pre.textContent = String(err || 'Could not load YAML file.');
            }
        });
    }

    function openCommentEditor(action) {
        if (!state.currentFailure || !state.currentFailure.data) return;
        var label = document.getElementById('ac-failure-comment-label');
        var saveBtn = document.getElementById('ac-btn-save-comment');
        var input = document.getElementById('ac-failure-comment');
        if (!label || !saveBtn || !input) return;

        var data = state.currentFailure.data || {};
        var existing = '';
        if (action === 'override' && eventEnabled(data.override)) {
            existing = String(data.override.comment || '');
        }
        if (action === 'monitor' && eventEnabled(data.monitor)) {
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

        renderFailureHeader(key, failure, state.currentFailureKind);
        renderFailureMeta(
            state.currentCard || loaded,
            key,
            failure,
            state.currentFailureKind
        );
        document.getElementById('ac-failure-message').textContent =
            failure.message || '';
        updateToggleLabels(failure, state.currentFailureKind);
        applyOverridePolicy(key, state.currentFailureKind);
        updateCommentBoxState();
        renderFailurePath(
            loaded.__path__
            || (state.currentCard && state.currentCard.path)
            || ''
        );
        renderFailureDocLink(key, failure.name || key);

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

    function showCheck(card, failureKey, failure, kind) {
        state.currentCard = card;
        state.currentFailure = {
            key: failureKey,
            data: failure,
        };
        state.currentFailureKind = kind === 'pass' ? 'pass' : 'failure';
        state.pendingAction = '';
        renderFailureHeader(
            failureKey,
            failure || {},
            state.currentFailureKind
        );
        renderFailureMeta(
            card,
            failureKey,
            failure || {},
            state.currentFailureKind
        );
        document.getElementById('ac-failure-message').textContent =
            failure.message || '';
        updateToggleLabels(failure || {}, state.currentFailureKind);
        applyOverridePolicy(failureKey, state.currentFailureKind);
        renderFailurePath(card && card.path ? card.path : '');
        renderFailureDocLink(failureKey, failure.name || failureKey);
        setFailureNote('', false);
        toggleCommentEditor(false);
        if (state.currentFailureKind === 'pass') {
            var btnOverride = document.getElementById('ac-btn-override');
            var btnMonitor = document.getElementById('ac-btn-monitor');
            var btnClear = document.getElementById('ac-btn-clear');
            if (btnOverride) btnOverride.disabled = true;
            if (btnMonitor) btnMonitor.disabled = true;
            if (btnClear) btnClear.disabled = true;
        }
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

    function buildObsdirTestsHtml(card) {
        var cardJson = jsonAttr(card || {});
        var failures = Array.isArray(card && card.visible_failures)
            ? card.visible_failures : [];
        var passes = Array.isArray(card && card.visible_passes)
            ? card.visible_passes : [];
        var html = '';

        failures.forEach(function (pair) {
            var key = pair[0];
            var failure = pair[1] || {};
            html += '<button class="ac-check-pill ac-check-pill--failed"' +
                ' data-ac-action="failure"' +
                ' data-ac-failure="' + jsonAttr(failure) + '"' +
                ' data-ac-failure-key="' + esc(key || '') + '"' +
                ' data-ac-obsdir="' + esc(card.obsdir || '') + '"' +
                ' data-ac-card="' + cardJson + '">';
            html += '<span class="ac-check-pill__icons ' +
                'ac-check-pill__icons--start">' +
                '<i class="fa-solid fa-xmark ac-i-bad"></i></span>';
            html += '<span class="ac-check-pill__label">' +
                esc((failure.type || '') + ':' +
                    (failure.name || key || '')) + '</span>';
            html += '<span class="ac-check-pill__icons">';
            if (eventEnabled(failure.monitor)) {
                html += '<i class="fa-solid fa-bell ac-i-mon"></i>';
            }
            if (eventEnabled(failure.override)) {
                html += '<i class="fa-solid fa-triangle-exclamation ' +
                    'ac-i-ovr"></i>';
            }
            html += '</span></button>';
        });

        if (state.showPassed) {
            passes.forEach(function (pair) {
                var key = pair[0];
                var passed = pair[1] || {};
                html += '<button class="ac-check-pill ac-check-pill--passed"' +
                    ' data-ac-action="pass"' +
                    ' data-ac-pass="' + jsonAttr(passed) + '"' +
                    ' data-ac-pass-key="' + esc(key || '') + '"' +
                    ' data-ac-obsdir="' + esc(card.obsdir || '') + '"' +
                    ' data-ac-card="' + cardJson + '">';
                html += '<span class="ac-check-pill__icons ' +
                    'ac-check-pill__icons--start">' +
                    '<i class="fa-solid fa-check ac-i-pass"></i></span>';
                html += '<span class="ac-check-pill__label">' +
                    esc((passed.type || '') + ':' +
                        (passed.name || key || '')) + '</span>';
                html += '<span class="ac-check-pill__icons"></span>';
                html += '</button>';
            });
        }

        if (!html) {
            html = '<span class="ac-check-empty">No visible checks</span>';
        }
        return html;
    }

    function renderObsdirOverlayButtons() {
        function setButton(id, onClass, onLabel, offLabel, isOn, icon) {
            var btn = document.getElementById(id);
            if (!btn) return;
            btn.classList.toggle(onClass, !!isOn);
            btn.innerHTML = '<i class="fa-solid ' + icon + '"></i> ' +
                (isOn ? onLabel : offLabel);
        }
        setButton(
            'ac-obsdir-btn-overridden',
            'ac-toggle-override-on',
            'Hide overridden checks',
            'Show overridden checks',
            state.showOverridden,
            'fa-layer-group'
        );
        setButton(
            'ac-obsdir-btn-monitored',
            'ac-toggle-monitor-on',
            'Hide monitored checks',
            'Show monitored checks',
            state.showMonitored,
            'fa-bell-concierge'
        );
        setButton(
            'ac-obsdir-btn-passed',
            'ac-toggle-pass-on',
            'Hide passed checks',
            'Show passed checks',
            state.showPassed,
            'fa-check'
        );
    }

    function openObsdirOverlay(card) {
        if (!card || !card.obsdir) return;
        state.currentObsdirCard = card;
        var title = document.getElementById('ac-obsdir-title');
        var meta = document.getElementById('ac-obsdir-meta');
        var tests = document.getElementById('ac-obsdir-tests');
        if (title) {
            title.textContent =
                'APERO Check information: ' + String(card.obsdir || '');
        }
        if (meta) {
            meta.innerHTML =
                '<div class="ac-failure-meta-row"><strong>Obsdir:</strong> ' +
                esc(card.obsdir || '') + '</div>' +
                '<div class="ac-failure-meta-row"><strong>Result:</strong> ' +
                esc(card.status === 'ok' ? 'Passed' : 'Failed') + '</div>' +
                '<div class="ac-failure-meta-row"><strong>Last run:</strong> ' +
                esc(card.last_run || 'n/a') + '</div>';
        }
        if (tests) {
            tests.innerHTML = buildObsdirTestsHtml(card);
        }
        renderObsdirOverlayButtons();
        syncAdvancedModeUi();
        openOverlay('ac-obsdir-overlay');
    }

    function refreshAndReopenObsdir(extra, obsdir) {
        state.reopenObsdirOnRefresh = String(obsdir || '').trim();
        return refreshUrl(extra).then(function () {
            var target = state.reopenObsdirOnRefresh;
            state.reopenObsdirOnRefresh = '';
            if (!target) return;
            var card = cardForObsdir(target);
            if (card) {
                openObsdirOverlay(card);
            }
        });
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
            showCheck(
                JSON.parse(btn.getAttribute('data-ac-card') || '{}'),
                btn.getAttribute('data-ac-failure-key') || '',
                JSON.parse(btn.getAttribute('data-ac-failure') || '{}'),
                'failure'
            );
        } else if (action === 'pass') {
            showCheck(
                JSON.parse(btn.getAttribute('data-ac-card') || '{}'),
                btn.getAttribute('data-ac-pass-key') || '',
                JSON.parse(btn.getAttribute('data-ac-pass') || '{}'),
                'pass'
            );
        } else if (action === 'issue') {
            showIssue(JSON.parse(btn.getAttribute('data-ac-card') || '{}'));
        } else if (action === 'rerun-night') {
            requestRerunNight(
                JSON.parse(btn.getAttribute('data-ac-card') || '{}')
            );
        } else if (action === 'delete-night') {
            requestDeleteNight(
                JSON.parse(btn.getAttribute('data-ac-card') || '{}')
            );
        }
    });

    document.addEventListener('click', function (ev) {
        var cardEl = ev.target.closest('#ac-card-list .ac-card');
        if (!cardEl) return;
        if (ev.target.closest('[data-ac-action]')) return;
        if (ev.target.closest('a,button,input,select,textarea,label')) return;
        var card = {};
        try {
            card = JSON.parse(cardEl.getAttribute('data-ac-card') || '{}');
        } catch (_err) {
            card = {};
        }
        if (!card.obsdir) {
            card = cardForObsdir(cardEl.getAttribute('data-obsdir') || '');
        }
        if (card) {
            openObsdirOverlay(card);
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
            if (!isOverrideAllowed(state.currentFailure.key)) {
                setFailureNote(
                    'Override is disabled by global policy for this check.',
                    true
                );
                return;
            }
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

    var btnViewYaml = document.getElementById('ac-btn-view-yaml');
    if (btnViewYaml) {
        btnViewYaml.addEventListener('click', function () {
            openYamlViewer();
        });
    }

    var yamlSearch = document.getElementById('ac-yaml-search');
    if (yamlSearch) {
        yamlSearch.addEventListener('input', function () {
            renderYamlText();
        });
    }

    var btnYamlCopy = document.getElementById('ac-btn-yaml-copy');
    if (btnYamlCopy) {
        btnYamlCopy.addEventListener('click', function () {
            copyText(String(state.yamlRawText || '')).then(function () {
                var count = document.getElementById('ac-yaml-match-count');
                if (count) {
                    count.textContent = 'YAML copied to clipboard';
                }
            }).catch(function () {
                var count = document.getElementById('ac-yaml-match-count');
                if (count) {
                    count.textContent = 'Could not copy YAML';
                }
            });
        });
    }

    var btnRerunCheck = document.getElementById('ac-btn-rerun-check');
    if (btnRerunCheck) {
        btnRerunCheck.addEventListener('click', function () {
            if (!state.currentCard || !state.currentFailure) return;
            var baseline = String(state.currentCard.last_run || '').trim();
            postJson(cfg.apiRerunCheckUrl, {
                profile_id: cfg.profileId,
                obsdir: state.currentCard.obsdir,
                check_key: state.currentFailure.key,
            }).then(function (data) {
                var taskId = String(data.task_id || '').trim();
                if (taskId) {
                    setFailureNote(
                        'Check re-run queued (task: ' + taskId + ').',
                        false
                    );
                } else {
                    setFailureNote('Check re-run queued.', false);
                }
                waitForRerunCompletion(
                    state.currentCard.obsdir,
                    baseline,
                    function (latest) {
                        if (state.currentCard) {
                            state.currentCard.last_run = latest;
                        }
                        if (state.currentFailure && state.currentFailure.data) {
                            state.currentFailure.data.last_run = latest;
                            renderFailureMeta(
                                state.currentCard || {},
                                state.currentFailure.key,
                                state.currentFailure.data,
                                state.currentFailureKind
                            );
                        }
                        setFailureNote(
                            'Check re-run finished. Last run: ' + latest,
                            false
                        );
                        window.setTimeout(function () {
                            window.location.reload();
                        }, 900);
                    }
                );
            }).catch(function (err) {
                setFailureNote(
                    String(err || 'Could not queue this check.'),
                    true
                );
            });
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
            state.cardsByPage = {};
            loadAndRender(state.page, true);
        });
    }

    var btnShowTests = document.getElementById('ac-btn-show-tests');
    if (btnShowTests) {
        btnShowTests.addEventListener('click', function () {
            state.showTests = !state.showTests;
            syncToggleButtons();
            syncShowTestsUi();
        });
    }

    var obsBtnOverridden = document.getElementById('ac-obsdir-btn-overridden');
    if (obsBtnOverridden) {
        obsBtnOverridden.addEventListener('click', function () {
            var card = state.currentObsdirCard;
            if (!card || !card.obsdir) return;
            refreshAndReopenObsdir({
                show_overridden: state.showOverridden ? '0' : '1',
                page: '1',
            }, card.obsdir);
        });
    }

    var obsBtnMonitored = document.getElementById('ac-obsdir-btn-monitored');
    if (obsBtnMonitored) {
        obsBtnMonitored.addEventListener('click', function () {
            var card = state.currentObsdirCard;
            if (!card || !card.obsdir) return;
            refreshAndReopenObsdir({
                show_monitored: state.showMonitored ? '0' : '1',
                page: '1',
            }, card.obsdir);
        });
    }

    var obsBtnPassed = document.getElementById('ac-obsdir-btn-passed');
    if (obsBtnPassed) {
        obsBtnPassed.addEventListener('click', function () {
            var card = state.currentObsdirCard;
            if (!card || !card.obsdir) return;
            refreshAndReopenObsdir({
                show_passed: state.showPassed ? '0' : '1',
                page: '1',
            }, card.obsdir);
        });
    }

    var obsBtnAdvanced = document.getElementById('ac-obsdir-btn-advanced');
    if (obsBtnAdvanced) {
        obsBtnAdvanced.addEventListener('click', function () {
            state.advancedMode = !state.advancedMode;
            syncAdvancedModeUi();
        });
    }

    var obsBtnRerun = document.getElementById('ac-obsdir-btn-rerun');
    if (obsBtnRerun) {
        obsBtnRerun.addEventListener('click', function () {
            if (!state.currentObsdirCard) return;
            requestRerunNight(state.currentObsdirCard);
        });
    }

    var obsBtnHistory = document.getElementById('ac-obsdir-btn-history');
    if (obsBtnHistory) {
        obsBtnHistory.addEventListener('click', function () {
            if (!state.currentObsdirCard) return;
            showHistory(state.currentObsdirCard);
        });
    }

    var obsBtnIssue = document.getElementById('ac-obsdir-btn-issue');
    if (obsBtnIssue) {
        obsBtnIssue.addEventListener('click', function () {
            if (!state.currentObsdirCard) return;
            showIssue(state.currentObsdirCard);
        });
    }

    var btnAdvanced = document.getElementById('ac-btn-advanced');
    if (btnAdvanced) {
        btnAdvanced.addEventListener('click', function () {
            state.advancedMode = !state.advancedMode;
            syncAdvancedModeUi();
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
                show_overridden: state.showOverridden ? '0' : '1',
                page: '1',
            });
        });
    }

    var btnMonitored = document.getElementById('ac-btn-monitored');
    if (btnMonitored) {
        btnMonitored.addEventListener('click', function () {
            refreshUrl({
                show_monitored: state.showMonitored ? '0' : '1',
                page: '1',
            });
        });
    }

    var btnPassed = document.getElementById('ac-btn-passed');
    if (btnPassed) {
        btnPassed.addEventListener('click', function () {
            refreshUrl({
                show_passed: state.showPassed ? '0' : '1',
                page: '1',
            });
        });
    }

    var typeSel = document.getElementById('ac-type');
    if (typeSel) {
        typeSel.addEventListener('change', function () {
            refreshUrl({ type: typeSel.value, page: '1' });
        });
    }

    var resultSel = document.getElementById('ac-result-filter');
    if (resultSel) {
        resultSel.addEventListener('change', function () {
            refreshUrl({
                result_filter: resultSel.value || 'all',
                page: '1',
            });
        });
    }

    var obsdirFilter = document.getElementById('ac-obsdir-filter');
    if (obsdirFilter) {
        obsdirFilter.addEventListener('input', function () {
            if (state.filterTimer) {
                window.clearTimeout(state.filterTimer);
            }
            state.filterTimer = window.setTimeout(function () {
                refreshUrl({
                    obsdir_filter: obsdirFilter.value || '',
                    page: '1',
                });
            }, 250);
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

    var pageSel = document.getElementById('ac-page-select');
    if (pageSel) {
        pageSel.addEventListener('change', function () {
            refreshUrl({ page: pageSel.value || '1' });
        });
    }

    ['ac-page-prev-top', 'ac-page-prev-bottom'].forEach(function (id) {
        var btn = document.getElementById(id);
        if (!btn) return;
        btn.addEventListener('click', function () {
            if (state.page > 1) {
                refreshUrl({ page: String(state.page - 1) });
            }
        });
    });

    ['ac-page-next-top', 'ac-page-next-bottom'].forEach(function (id) {
        var btn = document.getElementById(id);
        if (!btn) return;
        btn.addEventListener('click', function () {
            if (state.page < state.totalPages) {
                refreshUrl({ page: String(state.page + 1) });
            }
        });
    });

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

    state.cardsByPage[String(state.page)] = Array.isArray(cfg.cards)
        ? cfg.cards.slice() : [];
    syncStateFromQuery();
    syncToggleButtons();
    syncShowTestsUi();
    syncAdvancedModeUi();
    renderPageControls();
    loadAndRender(state.page, false);
}());
