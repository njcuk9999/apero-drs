(function () {
    'use strict';

    var cfg = window.AperoRejectionList || {};
    var tabs = Array.isArray(cfg.tabs) ? cfg.tabs : [];
    var canManageHistory = !!cfg.canManageHistory;
    if (!tabs.length) return;

    var state = {
        tab: tabs[0].key,
        page: 1,
        perPage: 50,
        sort: 'identifier_desc',
        filters: {
            identifier: '',
            pp: '',
            tel: '',
            rv: '',
            used: '',
            who: '',
            last_update: '',
            comment: ''
        },
        total: 0,
        pages: 0,
        historyPage: 1,
        historyPages: 0,
        historyPerPage: 50,
        historyQ: ''
    };
    var filterTimer = null;
    var historyTimer = null;

    function applyStateFromUrl() {
        var params = new URLSearchParams(window.location.search || '');
        var instrument = String(params.get('instrument') || '')
            .trim().toLowerCase();
        if (instrument) {
            for (var i = 0; i < tabs.length; i += 1) {
                var key = String(tabs[i].key || '').toLowerCase();
                if (instrument === key) {
                    state.tab = tabs[i].key;
                    break;
                }
            }
        }
        var identifier = String(params.get('identifier') || '').trim();
        if (identifier) {
            state.filters.identifier = identifier;
        }
    }

    function sortInfo() {
        var raw = String(state.sort || 'identifier_desc');
        var parts = raw.split('_');
        if (parts.length < 2) {
            return { key: 'identifier', dir: 'asc' };
        }
        var dir = parts.pop();
        var key = parts.join('_');
        if (dir !== 'asc' && dir !== 'desc') {
            dir = 'asc';
        }
        return { key: key, dir: dir };
    }

    function sortIcon(sortKey) {
        var info = sortInfo();
        if (info.key !== sortKey) {
            return '<i class="fa-solid fa-sort"></i>';
        }
        if (info.dir === 'desc') {
            return '<i class="fa-solid fa-sort-down"></i>';
        }
        return '<i class="fa-solid fa-sort-up"></i>';
    }

    function esc(value) {
        return String(value == null ? '' : value).replace(
            /[<>&"']/g,
            function (char) {
                return ({
                    '<': '&lt;',
                    '>': '&gt;',
                    '&': '&amp;',
                    '"': '&quot;',
                    "'": '&#39;'
                })[char];
            }
        );
    }

    function fmtTime(value) {
        return String(value || '').replace('T', ' ');
    }

    function prettyAction(value) {
        var action = String(value || '').trim().toLowerCase();
        if (!action) return 'Update';
        return action.charAt(0).toUpperCase() + action.slice(1);
    }

    function astrometricsIdentifierUrl(identifier) {
        return '/astrometrics?fo_tab=advanced&fo_source=header'
            + '&fo_property=IDENTIFIER'
            + '&fo_value=' + encodeURIComponent(String(identifier || ''))
            + '&fo_search=1';
    }

    function diffChipHtml(value, mode) {
        var text = String(value || '');
        var cls = 'rj-diff-chip rj-diff-chip--neutral';
        if (mode === 'add') cls = 'rj-diff-chip rj-diff-chip--add';
        if (mode === 'remove') cls = 'rj-diff-chip rj-diff-chip--remove';
        if (!text) {
            text = '(empty)';
        }
        return '<span class="' + cls + '">'
            + esc(text).replace(/\n/g, '<br>') + '</span>';
    }

    function renderDiffCard(key, previous, next) {
        var prevHtml = diffChipHtml(previous, 'neutral');
        var nextHtml = diffChipHtml(next, 'neutral');
        if (!previous && next) {
            nextHtml = diffChipHtml(next, 'add');
        } else if (previous && !next) {
            prevHtml = diffChipHtml(previous, 'remove');
        }
        return '<div class="rj-diff-card">'
            + '<h4 class="rj-diff-card__title">' + esc(key) + '</h4>'
            + '<div class="rj-diff-card__row">'
            + '<span class="rj-diff-card__label">Was</span>'
            + prevHtml + '</div>'
            + '<div class="rj-diff-card__row">'
            + '<span class="rj-diff-card__label">Now</span>'
            + nextHtml + '</div></div>';
    }

    function setStatus(id, html) {
        var el = document.getElementById(id);
        if (el) el.innerHTML = html || '';
    }

    function showOverlay(id, show) {
        var el = document.getElementById(id);
        if (el) el.hidden = !show;
    }

    function setMainView(mode) {
        var listCard = document.getElementById('rj-list-card');
        var histCard = document.getElementById('rj-history-card');
        var showHistory = mode === 'history';
        if (listCard) {
            listCard.hidden = showHistory;
            listCard.style.display = showHistory ? 'none' : '';
        }
        if (histCard) {
            histCard.hidden = !showHistory;
            histCard.style.display = showHistory ? '' : 'none';
        }
    }

    function updateTabButtons(active) {
        document.querySelectorAll('[data-rj-tab]').forEach(function (btn) {
            btn.classList.toggle(
                'rj-htab--active',
                btn.getAttribute('data-rj-tab') === active
            );
        });
    }

    function currentTabLabel() {
        for (var i = 0; i < tabs.length; i += 1) {
            if (tabs[i].key === state.tab) return tabs[i].label;
        }
        return state.tab.toUpperCase();
    }

    function renderRows(rows) {
        var host = document.getElementById('rj-list');
        var count = document.getElementById('rj-count');
        var info = document.getElementById('rj-page-info');
        var prev = document.getElementById('rj-prev');
        var next = document.getElementById('rj-next');
        if (count) {
            count.textContent = state.total
                ? state.total + ' entries in ' + currentTabLabel()
                : '0 entries';
        }
        if (info) {
            info.textContent = state.pages
                ? state.page + ' of ' + state.pages
                : '0 of 0';
        }
        if (prev) prev.disabled = state.page <= 1;
        if (next) next.disabled = state.page >= state.pages;
        if (!host) return;
        host.innerHTML = '';

        var identVal = esc(state.filters.identifier || '');
        var whoVal = esc(state.filters.who || '');
        var lastVal = esc(state.filters.last_update || '');
        var commVal = esc(state.filters.comment || '');
        var ppVal = String(state.filters.pp || '');
        var telVal = String(state.filters.tel || '');
        var rvVal = String(state.filters.rv || '');
        var usedVal = String(state.filters.used || '');

        function binaryFilterOptions(selected) {
            var anySel = selected === '' ? ' selected' : '';
            var oneSel = selected === '1' ? ' selected' : '';
            var zeroSel = selected === '0' ? ' selected' : '';
            return '<option value=""' + anySel + '>Any</option>'
                + '<option value="1"' + oneSel + '>1</option>'
                + '<option value="0"' + zeroSel + '>0</option>';
        }

        function sortHeader(label, key) {
            var info = sortInfo();
            var dir = info.key === key ? info.dir : '';
            return '<button type="button" class="rj-th-sort" '
                + 'data-sort-key="' + esc(key) + '" '
                + 'data-sort-dir="' + esc(dir) + '">'
                + '<span>' + esc(label) + '</span>'
                + sortIcon(key)
                + '</button>';
        }

        var html = '<div class="rj-table-wrap">'
            + '<table class="ari-dt rj-table">'
            + '<thead class="ari-dt__header-row"><tr>'
            + '<th class="ari-dt__th">'
            + sortHeader('Identifier', 'identifier') + '</th>'
            + '<th class="ari-dt__th">' + sortHeader('PP', 'pp')
            + '</th>'
            + '<th class="ari-dt__th">' + sortHeader('TEL', 'tel')
            + '</th>'
            + '<th class="ari-dt__th">' + sortHeader('RV', 'rv')
            + '</th>'
            + '<th class="ari-dt__th">' + sortHeader('USED', 'used')
            + '</th>'
            + '<th class="ari-dt__th">' + sortHeader('Who', 'who')
            + '</th>'
            + '<th class="ari-dt__th">'
            + sortHeader('Last update', 'last_update') + '</th>'
            + '<th class="ari-dt__th">'
            + sortHeader('Comment', 'comment') + '</th>'
            + '<th class="ari-dt__th">Actions</th>'
            + '</tr>'
            + '<tr class="ari-dt__filter-row">'
            + '<th class="rj-filter-cell">'
            + '<input class="rj-filter-input" '
            + 'data-filter-key="identifier" type="search" '
            + 'placeholder="Filter" value="' + identVal + '"></th>'
            + '<th class="rj-filter-cell">'
            + '<select class="rj-filter-select" data-filter-key="pp">'
            + binaryFilterOptions(ppVal) + '</select></th>'
            + '<th class="rj-filter-cell">'
            + '<select class="rj-filter-select" data-filter-key="tel">'
            + binaryFilterOptions(telVal) + '</select></th>'
            + '<th class="rj-filter-cell">'
            + '<select class="rj-filter-select" data-filter-key="rv">'
            + binaryFilterOptions(rvVal) + '</select></th>'
            + '<th class="rj-filter-cell">'
            + '<select class="rj-filter-select" data-filter-key="used">'
            + binaryFilterOptions(usedVal) + '</select></th>'
            + '<th class="rj-filter-cell">'
            + '<input class="rj-filter-input" '
            + 'data-filter-key="who" type="search" '
            + 'placeholder="Filter" value="' + whoVal + '"></th>'
            + '<th class="rj-filter-cell">'
            + '<input class="rj-filter-input" '
            + 'data-filter-key="last_update" type="search" '
            + 'placeholder="Filter" value="' + lastVal + '"></th>'
            + '<th class="rj-filter-cell">'
            + '<input class="rj-filter-input" '
            + 'data-filter-key="comment" type="search" '
            + 'placeholder="Filter" value="' + commVal + '"></th>'
            + '<th class="rj-filter-cell"></th>'
            + '</tr></thead><tbody>';
        if (!rows.length) {
            html += '<tr class="ari-dt__row">'
                + '<td class="rj-empty" colspan="9">'
                + 'No entries match this filter.'
                + '</td></tr>';
        } else {
            rows.forEach(function (row) {
                var ident = String(row.IDENTIFIER || '');
                html += '<tr class="ari-dt__row">'
                    + '<td class="rj-cell-id"><a href="'
                    + esc(astrometricsIdentifierUrl(ident))
                    + '">' + esc(ident) + '</a></td>'
                    + '<td class="rj-cell-flg">' + esc(row.PP) + '</td>'
                    + '<td class="rj-cell-flg">' + esc(row.TEL) + '</td>'
                    + '<td class="rj-cell-flg">' + esc(row.RV) + '</td>'
                    + '<td class="rj-cell-flg">' + esc(row.USED) + '</td>'
                    + '<td>' + esc(row.WHO || '—') + '</td>'
                    + '<td class="rj-cell-ts">'
                    + esc(fmtTime(row.LAST_UPDATE || '—')) + '</td>'
                    + '<td class="rj-cell-comment" title="'
                    + esc(row.COMMENT || '') + '">'
                    + esc(row.COMMENT || '—')
                    + '</td>'
                    + '<td class="rj-cell-actions">'
                    + '<button type="button" class="rj-btn-icon" '
                    + 'data-action="edit" data-ident="'
                    + esc(row.IDENTIFIER) + '" title="Edit entry">'
                    + '<i class="fa-solid fa-pen"></i></button> '
                    + '<button type="button" '
                    + 'class="rj-btn-icon rj-btn-icon--danger" '
                    + 'data-action="delete" data-ident="'
                    + esc(row.IDENTIFIER) + '" title="Delete entry">'
                    + '<i class="fa-solid fa-trash"></i></button>'
                    + '</td>'
                    + '</tr>';
            });
        }
        html += '</tbody></table></div>';
        host.innerHTML = html;

        host.querySelectorAll('[data-action="edit"]').forEach(
            function (btn) {
                btn.addEventListener('click', function () {
                    var ident = btn.getAttribute('data-ident');
                    for (var i = 0; i < rows.length; i += 1) {
                        if (String(rows[i].IDENTIFIER) === String(ident)) {
                            openEditOverlay(rows[i]);
                            break;
                        }
                    }
                });
            }
        );
        host.querySelectorAll('[data-action="delete"]').forEach(
            function (btn) {
                btn.addEventListener('click', function () {
                    var ident = btn.getAttribute('data-ident');
                    for (var i = 0; i < rows.length; i += 1) {
                        if (String(rows[i].IDENTIFIER) === String(ident)) {
                            deleteRow(rows[i]);
                            break;
                        }
                    }
                });
            }
        );

        host.querySelectorAll('[data-sort-key]').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var key = String(btn.getAttribute('data-sort-key') || '');
                if (!key) return;
                var info = sortInfo();
                var dir = 'asc';
                if (info.key === key) {
                    dir = info.dir === 'asc' ? 'desc' : 'asc';
                }
                state.sort = key + '_' + dir;
                state.page = 1;
                loadRows();
            });
        });

        host.querySelectorAll('[data-filter-key]').forEach(function (input) {
            var key = String(input.getAttribute('data-filter-key') || '');
            if (!key) return;
            var isText = input.tagName.toLowerCase() === 'input';
            var eventName = isText ? 'input' : 'change';
            input.addEventListener(eventName, function () {
                var apply = function () {
                    state.filters[key] = String(input.value || '').trim();
                    state.page = 1;
                    loadRows();
                };
                if (!isText) {
                    apply();
                    return;
                }
                if (filterTimer) window.clearTimeout(filterTimer);
                filterTimer = window.setTimeout(apply, 250);
            });
        });
    }

    function loadRows() {
        setMainView('list');
        setStatus('rj-status',
            '<i class="fa-solid fa-spinner fa-spin"></i> Loading...');
        var params = new URLSearchParams();
        params.set('instrument', state.tab);
        params.set('page', state.page);
        params.set('per_page', state.perPage);
        params.set('sort', state.sort);
        Object.keys(state.filters).forEach(function (key) {
            if (state.filters[key] !== '') {
                params.set(key, state.filters[key]);
            }
        });
        fetch('/api/rejection-list/list?' + params.toString(), {
            credentials: 'same-origin'
        }).then(function (resp) {
            return resp.json().then(function (body) {
                return { ok: resp.ok, body: body };
            });
        }).then(function (res) {
            if (!res.body || !res.body.success) {
                setStatus('rj-status', 'Failed: '
                    + esc((res.body && res.body.error) || 'unknown'));
                return;
            }
            state.total = res.body.total || 0;
            state.pages = res.body.pages || 0;
            state.page = res.body.page || 1;
            setStatus('rj-status', '');
            renderRows(res.body.rows || []);
        }).catch(function (err) {
            setStatus('rj-status', 'Failed: ' + esc(err));
        });
    }

    function openEditOverlay(row) {
        document.getElementById('rj-edit-mode').value = row ? 'edit' : 'add';
        document.getElementById('rj-edit-original').value = row
            ? String(row.IDENTIFIER || '') : '';
        document.getElementById('rj-edit-title').textContent = row
            ? 'Edit rejection entry'
            : 'Add rejection entry';
        document.getElementById('rj-identifier').value = row
            ? String(row.IDENTIFIER || '') : '';
        document.getElementById('rj-pp').value = String(row ? row.PP : 1);
        document.getElementById('rj-tel').value = String(row ? row.TEL : 1);
        document.getElementById('rj-rv').value = String(row ? row.RV : 1);
        document.getElementById('rj-used').value = String(row ? row.USED : 1);
        document.getElementById('rj-comment').value = row
            ? String(row.COMMENT || '') : '';
        setStatus('rj-edit-status', '');
        showOverlay('rj-edit-overlay', true);
        document.getElementById('rj-identifier').focus();
    }

    function collectEditPayload() {
        var payload = {
            instrument: state.tab,
            identifier: document.getElementById('rj-identifier').value.trim(),
            IDENTIFIER: document.getElementById('rj-identifier').value.trim(),
            PP: document.getElementById('rj-pp').value,
            TEL: document.getElementById('rj-tel').value,
            RV: document.getElementById('rj-rv').value,
            USED: document.getElementById('rj-used').value,
            COMMENT: document.getElementById('rj-comment').value.trim()
        };
        return payload;
    }

    function saveRow(forceReplace) {
        var mode = document.getElementById('rj-edit-mode').value;
        var payload = collectEditPayload();
        if (!payload.IDENTIFIER) {
            setStatus('rj-edit-status', 'Identifier is required.');
            return;
        }
        if (mode === 'edit') {
            payload.old_identifier =
                document.getElementById('rj-edit-original').value;
        }
        if (forceReplace) payload.replace_existing = true;
        var url = mode === 'edit'
            ? '/api/rejection-list/update'
            : '/api/rejection-list/add';
        setStatus('rj-edit-status',
            '<i class="fa-solid fa-spinner fa-spin"></i> Saving...');
        fetch(url, {
            method: 'POST',
            credentials: 'same-origin',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        }).then(function (resp) {
            return resp.json().then(function (body) {
                return { ok: resp.ok, status: resp.status, body: body };
            });
        }).then(function (res) {
            if (res.status === 409 && res.body
                    && res.body.requires_confirmation) {
                var question = 'Identifier already exists in '
                    + currentTabLabel() + '. Replace it?';
                if (window.confirm(question)) {
                    saveRow(true);
                } else {
                    setStatus('rj-edit-status', 'Replacement cancelled.');
                }
                return;
            }
            if (!res.body || !res.body.success) {
                setStatus('rj-edit-status', 'Failed: '
                    + esc((res.body && res.body.error) || 'unknown'));
                return;
            }
            showOverlay('rj-edit-overlay', false);
            loadRows();
        }).catch(function (err) {
            setStatus('rj-edit-status', 'Failed: ' + esc(err));
        });
    }

    function deleteRow(row) {
        if (!window.confirm('Delete ' + row.IDENTIFIER + ' from '
                + currentTabLabel() + '?')) {
            return;
        }
        setStatus('rj-status',
            '<i class="fa-solid fa-spinner fa-spin"></i> Deleting...');
        fetch('/api/rejection-list/delete', {
            method: 'POST',
            credentials: 'same-origin',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                instrument: state.tab,
                identifier: row.IDENTIFIER
            })
        }).then(function (resp) {
            return resp.json().then(function (body) {
                return { ok: resp.ok, body: body };
            });
        }).then(function (res) {
            if (!res.body || !res.body.success) {
                setStatus('rj-status', 'Failed: '
                    + esc((res.body && res.body.error) || 'unknown'));
                return;
            }
            loadRows();
        }).catch(function (err) {
            setStatus('rj-status', 'Failed: ' + esc(err));
        });
    }

    function submitUpload(forceReplace) {
        var fileEl = document.getElementById('rj-upload-file');
        if (!fileEl.files || !fileEl.files[0]) {
            setStatus('rj-upload-status', 'Select a CSV file first.');
            return;
        }
        var fd = new FormData();
        fd.append('instrument', state.tab);
        fd.append('file', fileEl.files[0]);
        if (forceReplace) fd.append('replace_existing', '1');
        setStatus('rj-upload-status',
            '<i class="fa-solid fa-spinner fa-spin"></i> Uploading...');
        fetch('/api/rejection-list/upload', {
            method: 'POST',
            credentials: 'same-origin',
            body: fd
        }).then(function (resp) {
            return resp.json().then(function (body) {
                return { ok: resp.ok, status: resp.status, body: body };
            });
        }).then(function (res) {
            if (res.status === 409 && res.body
                    && res.body.requires_confirmation) {
                var msg = 'Upload has ' + (res.body.conflict_count || 0)
                    + ' existing identifiers in ' + currentTabLabel()
                    + '. Replace all of them?';
                if (window.confirm(msg)) {
                    submitUpload(true);
                } else {
                    setStatus('rj-upload-status', 'Upload cancelled.');
                }
                return;
            }
            if (!res.body || !res.body.success) {
                var details = '';
                if (res.body && Array.isArray(res.body.details)) {
                    details = ' ' + res.body.details.join(' | ');
                }
                setStatus('rj-upload-status', 'Failed: '
                    + esc((res.body && res.body.error) || 'unknown')
                    + esc(details));
                return;
            }
            setStatus('rj-upload-status', '');
            showOverlay('rj-upload-overlay', false);
            fileEl.value = '';
            loadRows();
        }).catch(function (err) {
            setStatus('rj-upload-status', 'Failed: ' + esc(err));
        });
    }

    function renderHistory(rows) {
        var host = document.getElementById('rj-history-list');
        var info = document.getElementById('rj-history-page');
        var prev = document.getElementById('rj-history-prev');
        var next = document.getElementById('rj-history-next');
        if (info) {
            info.textContent = state.historyPages
                ? state.historyPage + ' of ' + state.historyPages
                : '0 of 0';
        }
        if (prev) prev.disabled = state.historyPage <= 1;
        if (next) next.disabled = state.historyPage >= state.historyPages;
        if (!host) return;
        host.innerHTML = '';
        if (!rows.length) {
            host.innerHTML = '<div class="rj-empty">'
                + 'No history entries match this filter.</div>';
            return;
        }

        var html = '<div class="rj-table-wrap">'
            + '<table class="ari-dt rj-table">'
            + '<thead class="ari-dt__header-row"><tr>'
            + '<th class="ari-dt__th">Timestamp</th>'
            + '<th class="ari-dt__th">User</th>'
            + '<th class="ari-dt__th">Instrument</th>'
            + '<th class="ari-dt__th">Kind</th>'
            + '<th class="ari-dt__th">Identifier</th>'
            + '<th class="ari-dt__th">Fields</th>'
            + '<th class="ari-dt__th">Actions</th>'
            + '</tr></thead><tbody>';
        rows.forEach(function (row) {
            var fields = (row.fields || []).slice();
            if (row.previous_identifier) {
                fields.unshift('from ' + row.previous_identifier);
            }
            html += '<tr class="ari-dt__row">'
                + '<td class="rj-cell-ts">'
                + esc(fmtTime(row.timestamp || '')) + '</td>'
                + '<td>' + esc(row.user || '') + '</td>'
                + '<td>' + esc(row.instrument || '') + '</td>'
                + '<td>' + esc(prettyAction(row.action || '')) + '</td>'
                + '<td class="rj-cell-id">' + esc(row.identifier || '')
                + '</td>'
                + '<td class="rj-cell-comment" title="'
                + esc(fields.join(', ')) + '">'
                + esc(fields.join(', ') || '—') + '</td>'
                + '<td class="rj-cell-actions">'
                + '<button type="button" class="rj-btn-icon" '
                + 'data-action="view" data-hid="' + esc(row.id)
                + '" title="View change">'
                + '<i class="fa-solid fa-eye"></i></button> '
                + '<button type="button" class="rj-btn-icon" '
                + 'data-action="restore" data-hid="' + esc(row.id)
                + '" title="Restore this state">'
                + '<i class="fa-solid fa-clock-rotate-left"></i></button>'
                + (canManageHistory
                    ? ' <button type="button" '
                    + 'class="rj-btn-icon rj-btn-icon--danger" '
                    + 'data-action="delete-history" data-hid="'
                    + esc(row.id)
                    + '" title="Delete history entry">'
                    + '<i class="fa-solid fa-trash"></i></button>'
                    : '')
                + '</td></tr>';
        });
        html += '</tbody></table></div>';
        host.innerHTML = html;

        host.querySelectorAll('[data-action="view"]').forEach(
            function (btn) {
                btn.addEventListener('click', function () {
                    openHistoryEntry(btn.getAttribute('data-hid'));
                });
            }
        );
        host.querySelectorAll('[data-action="restore"]').forEach(
            function (btn) {
                btn.addEventListener('click', function () {
                    restoreHistoryEntry(btn.getAttribute('data-hid'));
                });
            }
        );
        host.querySelectorAll('[data-action="delete-history"]').forEach(
            function (btn) {
                btn.addEventListener('click', function () {
                    deleteHistoryEntry(btn.getAttribute('data-hid'));
                });
            }
        );
    }

    function parseJsonSafe(resp) {
        return resp.text().then(function (txt) {
            var body = null;
            try {
                body = JSON.parse(txt);
            } catch (err) {
                body = null;
            }
            return { ok: resp.ok, status: resp.status,
                body: body, raw: txt };
        });
    }

    function restoreHistoryEntry(id) {
        if (!window.confirm('Restore this rejection-list state?')) {
            return;
        }
        setStatus('rj-history-status',
            '<i class="fa-solid fa-spinner fa-spin"></i> Restoring...');

        function doRestore(url) {
            return fetch(url, {
                method: 'POST',
                credentials: 'same-origin',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: id })
            }).then(parseJsonSafe);
        }

        doRestore('/api/rejection-list/history/restore').then(function (res) {
            var needsLegacy = res.status === 404 || res.body === null;
            if (needsLegacy) {
                return doRestore('/api/rejection-list/history/resolve');
            }
            return res;
        }).then(function (res) {
            if (!res.body || !res.body.success) {
                var message = (res.body && res.body.error) || '';
                if (!message) {
                    message = 'HTTP ' + String(res.status || 'error');
                }
                setStatus('rj-history-status', 'Failed: ' + esc(message));
                return;
            }
            setStatus('rj-history-status',
                '<i class="fa-solid fa-check"></i> Restored.');
            loadHistory();
        }).catch(function (err) {
            setStatus('rj-history-status', 'Failed: ' + esc(err));
        });
    }

    function deleteHistoryEntry(id) {
        if (!canManageHistory) return;
        if (!window.confirm('Delete this history entry?')) {
            return;
        }
        setStatus('rj-history-status',
            '<i class="fa-solid fa-spinner fa-spin"></i> Deleting...');
        fetch('/api/rejection-list/history/delete', {
            method: 'POST',
            credentials: 'same-origin',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: id })
        }).then(parseJsonSafe).then(function (res) {
            if (!res.body || !res.body.success) {
                var message = (res.body && res.body.error) || '';
                if (!message) {
                    message = 'HTTP ' + String(res.status || 'error');
                }
                setStatus('rj-history-status', 'Failed: ' + esc(message));
                return;
            }
            setStatus('rj-history-status',
                '<i class="fa-solid fa-check"></i> Deleted.');
            loadHistory();
        }).catch(function (err) {
            setStatus('rj-history-status', 'Failed: ' + esc(err));
        });
    }

    function clearHistory() {
        if (!canManageHistory) return;
        if (!window.confirm('Clear ALL rejection history entries?')) {
            return;
        }
        setStatus('rj-history-status',
            '<i class="fa-solid fa-spinner fa-spin"></i> Clearing...');
        fetch('/api/rejection-list/history/clear', {
            method: 'POST',
            credentials: 'same-origin',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({})
        }).then(parseJsonSafe).then(function (res) {
            if (!res.body || !res.body.success) {
                var message = (res.body && res.body.error) || '';
                if (!message) {
                    message = 'HTTP ' + String(res.status || 'error');
                }
                setStatus('rj-history-status', 'Failed: ' + esc(message));
                return;
            }
            state.historyPage = 1;
            setStatus('rj-history-status',
                '<i class="fa-solid fa-check"></i> History cleared.');
            loadHistory();
        }).catch(function (err) {
            setStatus('rj-history-status', 'Failed: ' + esc(err));
        });
    }

    function loadHistory() {
        setMainView('history');
        setStatus('rj-history-status',
            '<i class="fa-solid fa-spinner fa-spin"></i> Loading...');
        var params = new URLSearchParams();
        params.set('page', state.historyPage);
        params.set('per_page', state.historyPerPage);
        if (state.historyQ) params.set('q', state.historyQ);
        fetch('/api/rejection-list/history/list?' + params.toString(), {
            credentials: 'same-origin'
        }).then(function (resp) {
            return resp.json().then(function (body) {
                return { ok: resp.ok, body: body };
            });
        }).then(function (res) {
            if (!res.body || !res.body.success) {
                setStatus('rj-history-status', 'Failed: '
                    + esc((res.body && res.body.error) || 'unknown'));
                return;
            }
            state.historyPages = res.body.pages || 0;
            state.historyPage = res.body.page || 1;
            setStatus('rj-history-status', '');
            renderHistory(res.body.rows || []);
        }).catch(function (err) {
            setStatus('rj-history-status', 'Failed: ' + esc(err));
        });
    }

    function openHistoryEntry(id) {
        setStatus('rj-history-status',
            '<i class="fa-solid fa-spinner fa-spin"></i> Loading entry...');
        fetch('/api/rejection-list/history/get?id=' + encodeURIComponent(id), {
            credentials: 'same-origin'
        }).then(function (resp) {
            return resp.json();
        }).then(function (body) {
            setStatus('rj-history-status', '');
            if (!body || !body.success) {
                setStatus('rj-history-status', 'Failed: '
                    + esc((body && body.error) || 'unknown'));
                return;
            }
            var entry = body.entry || {};
            var before = entry.before || {};
            var after = entry.after || {};
            var keys = {};
            Object.keys(before).forEach(function (key) { keys[key] = true; });
            Object.keys(after).forEach(function (key) { keys[key] = true; });
            var rows = Object.keys(keys).sort().map(function (key) {
                var b = before[key];
                var a = after[key];
                return renderDiffCard(key,
                    b == null ? '' : String(b),
                    a == null ? '' : String(a));
            }).join('');
            document.getElementById('rj-diff-title').textContent =
                'History entry for ' + (entry.identifier || '');
            document.getElementById('rj-diff-body').innerHTML = ''
                + '<div class="rj-history-card__time">'
                + esc(fmtTime(entry.timestamp || '')) + ' · '
                + esc(entry.user || '') + ' · '
                + esc(entry.instrument || '') + '</div>'
                + '<p style="margin:8px 0 12px 0; color:#57606a;">'
                + 'Changed fields rendered inline using the same add/remove '
                + 'colour treatment as astrometrics history.</p>'
                + '<div class="rj-diff-grid">' + rows + '</div>';
            showOverlay('rj-diff-overlay', true);
        }).catch(function (err) {
            setStatus('rj-history-status', 'Failed: ' + esc(err));
        });
    }

    document.querySelectorAll('[data-rj-tab]').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var tab = btn.getAttribute('data-rj-tab');
            updateTabButtons(tab);
            if (tab === 'history') {
                loadHistory();
                return;
            }
            state.tab = tab;
            state.page = 1;
            loadRows();
        });
    });

    document.addEventListener('click', function (event) {
        var close = event.target.closest('[data-rj-close]');
        if (!close) return;
        var which = close.getAttribute('data-rj-close');
        showOverlay('rj-' + which + '-overlay', false);
    });

    document.getElementById('rj-save').addEventListener('click', function () {
        saveRow(false);
    });

    document.getElementById('rj-open-upload').addEventListener(
        'click',
        function () {
            setStatus('rj-upload-status', '');
            showOverlay('rj-upload-overlay', true);
        }
    );

    var openAddBtn = document.getElementById('rj-open-add');
    if (openAddBtn) {
        openAddBtn.addEventListener('click', function () {
            openEditOverlay(null);
        });
    }

    document.getElementById('rj-upload-submit').addEventListener(
        'click',
        function () {
            submitUpload(false);
        }
    );

    document.getElementById('rj-per-page').addEventListener(
        'change',
        function (event) {
            state.perPage = Number(event.target.value || 50);
            state.page = 1;
            loadRows();
        }
    );

    document.getElementById('rj-prev').addEventListener('click', function () {
        if (state.page > 1) {
            state.page -= 1;
            loadRows();
        }
    });

    document.getElementById('rj-next').addEventListener('click', function () {
        if (state.page < state.pages) {
            state.page += 1;
            loadRows();
        }
    });

    if (cfg.canViewHistory) {
        var histFilter = document.getElementById('rj-history-filter');
        var histPer = document.getElementById('rj-history-per-page');
        var histPrev = document.getElementById('rj-history-prev');
        var histNext = document.getElementById('rj-history-next');
        var histClear = document.getElementById('rj-history-clear');
        if (histFilter) {
            histFilter.addEventListener(
            'input',
            function (event) {
                if (historyTimer) window.clearTimeout(historyTimer);
                historyTimer = window.setTimeout(function () {
                    state.historyQ = event.target.value || '';
                    state.historyPage = 1;
                    loadHistory();
                }, 250);
            }
            );
        }
        if (histPer) {
            histPer.addEventListener(
            'change',
            function (event) {
                state.historyPerPage = Number(event.target.value || 50);
                state.historyPage = 1;
                loadHistory();
            }
            );
        }
        if (histPrev) {
            histPrev.addEventListener(
            'click',
            function () {
                if (state.historyPage > 1) {
                    state.historyPage -= 1;
                    loadHistory();
                }
            }
            );
        }
        if (histNext) {
            histNext.addEventListener(
            'click',
            function () {
                if (state.historyPage < state.historyPages) {
                    state.historyPage += 1;
                    loadHistory();
                }
            }
            );
        }
        if (histClear) {
            histClear.addEventListener('click', clearHistory);
        }
    }

    applyStateFromUrl();
    updateTabButtons(state.tab);
    loadRows();
}());